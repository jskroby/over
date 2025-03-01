import streamlit as st
import time
import psutil
import subprocess
import sys
import os
import pandas as pd
import plotly.express as px
from agent_manager import AgentManager
from system_monitor import SystemMonitor
import logger_config
import logging
from database import init_db
from task_scheduler import TaskScheduler
from datetime import datetime, timedelta
from storage_handlers import StorageManager
import json

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="AI Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimalistic design with orange gradient
st.markdown("""
<style>
    /* Main theme */
    .main {
        background: linear-gradient(135deg, #1a1a1a, #0a0a0a);
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ff4b4b22, #ff8f1c22);
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #ff4b4b44;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(145deg, #ff4b4b, #ff8f1c);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }

    /* Headers */
    h1, h2, h3 {
        color: #ff4b4b;
        font-weight: 600;
    }

    /* Code editor */
    .stCodeEditor {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
agent_manager = AgentManager()
system_monitor = SystemMonitor()
task_scheduler = TaskScheduler()
storage_manager = StorageManager()
task_scheduler.start()

# Store current metrics
system_monitor.store_metrics()

# Title
st.title("🤖 AI Agent Dashboard")

# System Metrics
metrics = system_monitor.get_latest_metrics()
if metrics:
    # Create metrics history for visualization
    metrics_history = pd.DataFrame({
        'Time': [metrics.timestamp],
        'CPU': [metrics.cpu_usage],
        'Memory': [metrics.memory_usage]
    })

    # System metrics cards
    cols = st.columns(3)
    with cols[0]:
        st.metric("Status", "Active 🟢" if metrics.ollama_status else "Inactive 🔴")
    with cols[1]:
        st.metric("CPU", f"{metrics.cpu_usage}%")
    with cols[2]:
        st.metric("Memory", f"{metrics.memory_usage}%")

    # Performance graph
    st.plotly_chart(
        px.line(metrics_history,
                x='Time',
                y=['CPU', 'Memory'],
                title='System Performance',
                template='plotly_dark'),
        use_container_width=True
    )

# Agent Control
with st.expander("Agent Control", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 " + ("Stop Agents" if agent_manager.is_running() else "Start Agents")):
            if agent_manager.is_running():
                agent_manager.stop_agents()
                st.success("Agents stopped")
            else:
                agent_manager.start_agents()
                st.success("Agents started")

    with col2:
        if st.button("🔄 Restart Ollama"):
            system_monitor.restart_ollama()
            st.success("Ollama restarted")

# Code Management
with st.expander("Code Management", expanded=True):
    tabs = st.tabs(["Editor", "Deploy"])

    with tabs[0]:
        selected_agent = st.selectbox("Agent", agent_manager.agent_names)
        code_snippets = agent_manager.get_code_snippets(selected_agent)

        if code_snippets:
            selected_file = st.selectbox("File", [s.filename for s in code_snippets])
            code = next((s.content for s in code_snippets if s.filename == selected_file), "")

            edited_code = st.code_editor(code, language="python")
            if st.button("Save"):
                if agent_manager.save_code_snippet(selected_file, edited_code, "python", selected_agent):
                    st.success("Saved")

    with tabs[1]:
        deploy_agent = st.selectbox("Deploy Agent", agent_manager.agent_names)
        commit_msg = st.text_input("Commit Message")
        if st.button("Deploy"):
            if agent_manager.deploy_to_github(deploy_agent, [], commit_msg):
                st.success("Deployed")

# Task Scheduling
st.header("Task Scheduling")
with st.expander("Schedule Tasks", expanded=True):
    schedule_tabs = st.tabs(["Create Task", "View Tasks"])

    with schedule_tabs[0]:
        st.subheader("Create New Task")
        task_agent = st.selectbox("Select Agent", agent_manager.agent_names, key="schedule_agent")
        task_name = st.text_input("Task Name")
        task_description = st.text_area("Task Description")
        schedule_type = st.selectbox(
            "Schedule Type",
            ["once", "daily", "weekly", "monthly"],
            key="schedule_type"
        )

        # Schedule time selection
        schedule_date = st.date_input("Schedule Date")
        schedule_time = st.time_input("Schedule Time")
        schedule_datetime = datetime.combine(schedule_date, schedule_time)

        # Task parameters
        st.subheader("Task Parameters")
        param_key = st.text_input("Parameter Name")
        param_value = st.text_input("Parameter Value")
        parameters = {param_key: param_value} if param_key and param_value else {}

        if st.button("Schedule Task"):
            if task_scheduler.add_task(
                task_agent,
                task_name,
                task_description,
                schedule_type,
                schedule_datetime,
                parameters
            ):
                st.success("Task scheduled successfully!")
            else:
                st.error("Failed to schedule task")

    with schedule_tabs[1]:
        st.subheader("Scheduled Tasks")
        view_agent = st.selectbox("Filter by Agent", ["All"] + agent_manager.agent_names)

        tasks = task_scheduler.get_scheduled_tasks(
            None if view_agent == "All" else view_agent
        )

        if tasks:
            for task in tasks:
                with st.expander(f"{task.task_name} ({task.agent_name})"):
                    st.write(f"Description: {task.task_description}")
                    st.write(f"Schedule: {task.schedule_type}")
                    st.write(f"Next Run: {task.next_run}")
                    st.write(f"Last Run: {task.last_run or 'Never'}")
                    st.write(f"Status: {'Active' if task.is_active else 'Inactive'}")
                    if task.parameters:
                        st.write("Parameters:", task.parameters)
        else:
            st.info("No scheduled tasks found")


# Storage Integration Section
st.header("Storage Integration")
storage_col1, storage_col2 = st.columns(2)

with storage_col1:
    st.subheader("GitHub Integration")
    if 'github_token' not in st.session_state:
        if st.button("Login with GitHub"):
            auth_url = storage_manager.initialize_github_oauth()
            if auth_url:
                st.markdown(f"[Click here to authorize GitHub]({auth_url})")
            else:
                st.error("Failed to initialize GitHub OAuth")
    else:
        st.success("Connected to GitHub! ✓")
        if st.button("Logout from GitHub"):
            del st.session_state['github_token']
            st.rerun()

with storage_col2:
    st.subheader("Google Drive Integration")
    if 'gdrive_credentials' not in st.session_state:
        if st.button("Login with Google Drive"):
            auth_url = storage_manager.initialize_gdrive_oauth()
            if auth_url:
                st.markdown(f"[Click here to authorize Google Drive]({auth_url})")
            else:
                st.error("Failed to initialize Google Drive OAuth")
    else:
        st.success("Connected to Google Drive! ✓")
        if st.button("Logout from Google Drive"):
            del st.session_state['gdrive_credentials']
            st.rerun()

# Handle OAuth callbacks
st.query_params = st.experimental_get_query_params()
if 'code' in st.query_params:
    code = st.query_params['code'][0]
    if 'state' in st.query_params:  # GitHub callback
        if storage_manager.handle_github_callback(code, st.query_params['state'][0]):
            st.success("Successfully authenticated with GitHub!")
            st.rerun()
    else:  # Google Drive callback
        if storage_manager.handle_gdrive_callback(code):
            st.success("Successfully authenticated with Google Drive!")
            st.rerun()

# Backup section
if 'github_token' in st.session_state or 'gdrive_credentials' in st.session_state:
    st.header("Backup Agent Data")
    backup_col1, backup_col2 = st.columns(2)

    with backup_col1:
        backup_agent = st.selectbox("Select Agent to Backup", agent_manager.agent_names)

    with backup_col2:
        if st.button("Backup Agent Data"):
            if storage_manager.backup_agent_data(backup_agent, f"data/{backup_agent}"):
                st.success("Agent data backed up successfully!")
            else:
                st.error("Failed to backup agent data")

# Recent Activity
st.header("Recent Activity")
activity_tabs = st.tabs(["Agent Status", "Task History", "Logs"])

with activity_tabs[0]:
    # Agent Status
    for agent, info in agent_manager.get_agent_statuses().items():
        cols = st.columns([1, 2, 2])
        with cols[0]:
            st.write(f"**{agent}**")
        with cols[1]:
            st.write("🟢 Active" if info['status'] else "🔴 Inactive")
        with cols[2]:
            st.write(info['task'])

with activity_tabs[1]:
    # Task History
    for agent in agent_manager.agent_names:
        st.subheader(f"{agent}'s Tasks")
        conversations = agent_manager.get_agent_conversation(agent)
        if conversations:
            for msg in conversations:
                st.code(msg, language="plain")
        else:
            st.info("No task history yet")

with activity_tabs[2]:
    # Logs
    st.code("\n".join(logger_config.get_recent_logs()))

# Auto-refresh
time.sleep(5)
st.rerun()