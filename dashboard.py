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

# Agent Status
status = agent_manager.get_agent_statuses()
st.header("Agent Status")
for agent, info in status.items():
    cols = st.columns([1, 2, 2])
    with cols[0]:
        st.write(f"**{agent}**")
    with cols[1]:
        st.write("🟢 Active" if info['status'] else "🔴 Inactive")
    with cols[2]:
        st.write(info['task'])

# Agent Conversations
st.header("Agent Conversations")
for agent in agent_manager.agent_names:
    with st.expander(f"🤖 {agent} Conversation History", expanded=False):
        conversations = agent_manager.get_agent_conversation(agent)
        if conversations:
            for msg in conversations:
                st.code(msg, language="plain")
        else:
            st.info("No conversation history yet")


# Logs
with st.expander("Logs", expanded=False):
    st.code("\n".join(logger_config.get_recent_logs()))

# Auto-refresh
time.sleep(5)
st.rerun()