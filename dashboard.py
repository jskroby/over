import streamlit as st
import time
import psutil
import subprocess
import sys
import os
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
    layout="wide"
)

# Custom CSS for neumorphic design
st.markdown("""
<style>
    /* Neumorphic styles */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #1f1f1f, #252525);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 8px 8px 16px #151515, -8px -8px 16px #292929;
        margin: 10px 0;
    }

    .stButton > button {
        background: linear-gradient(145deg, #ff4b4b, #cc3c3c);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        box-shadow: 4px 4px 8px #151515, -4px -4px 8px #292929;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 6px 6px 12px #151515, -6px -6px 12px #292929;
    }

    /* Dark theme enhancements */
    .stTextInput > div > div {
        background-color: #252525;
        color: white;
        border-radius: 10px;
    }

    .stMarkdown {
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
agent_manager = AgentManager()
system_monitor = SystemMonitor()

# Store current metrics
system_monitor.store_metrics()

# Title and description
st.title("🤖 AI Agent Control Dashboard")
st.markdown("Monitor and control your AI agents running on Ollama")

# System Status Section
st.header("System Status")
col1, col2, col3 = st.columns(3)

metrics = system_monitor.get_latest_metrics()
if metrics:
    with col1:
        st.metric("Ollama Status", "Running 🟢" if metrics.ollama_status else "Stopped 🔴")

    with col2:
        st.metric("CPU Usage", f"{metrics.cpu_usage}%")

    with col3:
        st.metric("Memory Usage", f"{metrics.memory_usage}%")

# Folder Creation Section
st.header("Folder Management")
col1, col2 = st.columns(2)

with col1:
    folder_name = st.text_input("Enter folder name", key="folder_name")
    if st.button("Create Folder"):
        if folder_name:
            if agent_manager.create_folder(folder_name):
                st.success(f"Folder '{folder_name}' created successfully!")
            else:
                st.error("Failed to create folder")
        else:
            st.warning("Please enter a folder name")

# Agent Control Section
st.header("Agent Control")
col1, col2 = st.columns(2)

with col1:
    if st.button("Start Agents" if not agent_manager.is_running() else "Stop Agents"):
        if agent_manager.is_running():
            agent_manager.stop_agents()
            st.success("Agents stopped successfully!")
        else:
            agent_manager.start_agents()
            st.success("Agents started successfully!")

with col2:
    if st.button("Restart Ollama"):
        system_monitor.restart_ollama()
        st.success("Ollama restarted successfully!")

# Agent Status Section
st.header("Agent Status")
agent_statuses = agent_manager.get_agent_statuses()
for agent, status in agent_statuses.items():
    st.markdown(f"**{agent}**: {'🟢 Active' if status else '🔴 Inactive'}")

# Log Output Section
st.header("Log Output")
log_output = logger_config.get_recent_logs()

# Create an expandable container for logs
with st.expander("View Logs", expanded=True):
    log_text = "\n".join(log_output)
    st.code(log_text, language="plain")

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()