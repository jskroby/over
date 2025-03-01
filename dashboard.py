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
    initial_sidebar_state="expanded"
)

# Custom CSS for dynamic gradients and animations
st.markdown("""
<style>
    /* Main theme with animated gradient */
    .main {
        background: linear-gradient(-45deg, #1a1a1a, #0a0a0a, #2d1f1f, #1f2d1f);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Cabinet style navigation */
    .sidebar .sidebar-content {
        background: linear-gradient(165deg, #2d1f1f 0%, #1a1a1a 100%);
        box-shadow: 4px 0 8px rgba(0, 0, 0, 0.2);
    }

    /* Animated metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ff4b4b22, #ff8f1c22);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #ff4b4b44;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.1);
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 75, 75, 0.15);
    }

    /* Buttons with gradient animation */
    .stButton > button {
        background: linear-gradient(45deg, #ff4b4b, #ff8f1c);
        background-size: 200% 200%;
        animation: gradient 5s ease infinite;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.2);
    }

    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(255, 75, 75, 0.3);
    }

    /* Headers with gradient text */
    h1, h2, h3 {
        background: linear-gradient(45deg, #ff4b4b, #ff8f1c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }

    /* Card container */
    .card-container {
        background: linear-gradient(145deg, #1f1f1f66, #25252566);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
agent_manager = AgentManager()
system_monitor = SystemMonitor()
task_scheduler = TaskScheduler()
storage_manager = StorageManager()
task_scheduler.start()

# Sidebar Navigation
with st.sidebar:
    st.title("🤖 Agent Hub")

    # Profile Section
    st.image("https://picsum.photos/200", width=100)  # Placeholder profile image
    st.subheader("Welcome back!")

    # Navigation
    selected_page = st.radio(
        "Navigation",
        ["Dashboard", "My Agents", "Begin Project", "Work on Project", "Project Done", "Stats & Analytics"]
    )

# Main Content Area
if selected_page == "Dashboard":
    st.title("Dashboard Overview")

    # System Metrics
    metrics = system_monitor.get_latest_metrics()
    if metrics:
        # Create metrics history for visualization
        metrics_history = pd.DataFrame({
            'Time': [metrics.timestamp],
            'CPU': [metrics.cpu_usage],
            'Memory': [metrics.memory_usage]
        })

        # System metrics cards in a grid
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        cols = st.columns(3)
        with cols[0]:
            st.metric("System Status", "Active 🟢" if metrics.ollama_status else "Inactive 🔴")
        with cols[1]:
            st.metric("CPU Usage", f"{metrics.cpu_usage}%")
        with cols[2]:
            st.metric("Memory Usage", f"{metrics.memory_usage}%")
        st.markdown('</div>', unsafe_allow_html=True)

        # Performance graph
        st.plotly_chart(
            px.line(metrics_history,
                    x='Time',
                    y=['CPU', 'Memory'],
                    title='System Performance',
                    template='plotly_dark'),
            use_container_width=True
        )

elif selected_page == "My Agents":
    st.title("My Agents")

    # Agent Control Panel
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
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
        if st.button("🔄 Restart System"):
            system_monitor.restart_ollama()
            st.success("System restarted")
    st.markdown('</div>', unsafe_allow_html=True)

    # Agent Status and Tasks
    for agent in agent_manager.agent_names:
        st.markdown(f'<div class="card-container">', unsafe_allow_html=True)
        st.subheader(f"🤖 {agent}")
        status = agent_manager.get_agent_statuses()[agent]

        cols = st.columns([1, 2])
        with cols[0]:
            st.write("Status:", "🟢 Active" if status['status'] else "🔴 Inactive")
        with cols[1]:
            st.write("Current Task:", status['task'])

        # Show conversation history in a tab instead of nested expander
        task_tabs = st.tabs(["Conversation", "Code"])

        with task_tabs[0]:
            conversations = agent_manager.get_agent_conversation(agent)
            if conversations:
                for msg in conversations:
                    st.code(msg, language="plain")
            else:
                st.info("No conversation history yet")

        with task_tabs[1]:
            code_snippets = agent_manager.get_code_snippets(agent)
            if code_snippets:
                for snippet in code_snippets:
                    st.code(snippet.content, language="python")
            else:
                st.info("No code snippets yet")

        st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Begin Project":
    st.title("Begin New Project")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    project_name = st.text_input("Project Name")
    project_description = st.text_area("Project Description")
    assigned_agents = st.multiselect("Assign Agents", agent_manager.agent_names)
    if st.button("Start Project"):
        st.success("Project created successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Work on Project":
    st.title("Current Projects")
    st.info("Project management interface coming soon...")

elif selected_page == "Project Done":
    st.title("Completed Projects")
    st.info("Completed projects view coming soon...")

elif selected_page == "Stats & Analytics":
    st.title("Analytics Dashboard")
    st.info("Analytics dashboard coming soon...")

# Recent Activity
st.header("Recent Activity")
activity_tabs = st.tabs(["System Logs", "Agent Activities"])

with activity_tabs[0]:
    st.code("\n".join(logger_config.get_recent_logs()))

with activity_tabs[1]:
    for agent in agent_manager.agent_names:
        st.subheader(f"{agent}'s Recent Activities")
        conversations = agent_manager.get_agent_conversation(agent)
        if conversations:
            for msg in conversations[:5]:  # Show only last 5 activities
                st.code(msg, language="plain")
        else:
            st.info("No recent activities")

# Auto-refresh
time.sleep(5)
st.rerun()