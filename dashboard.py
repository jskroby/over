import streamlit as st
import time
import psutil
import subprocess
import sys
from agent_manager import AgentManager
from system_monitor import SystemMonitor
import logger_config
import logging

# Page config
st.set_page_config(
    page_title="AI Agent Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Initialize managers
agent_manager = AgentManager()
system_monitor = SystemMonitor()

# Title and description
st.title("🤖 AI Agent Control Dashboard")
st.markdown("Monitor and control your AI agents running on Ollama")

# System Status Section
st.header("System Status")
col1, col2, col3 = st.columns(3)

with col1:
    ollama_status = system_monitor.check_ollama_status()
    st.metric("Ollama Status", "Running 🟢" if ollama_status else "Stopped 🔴")

with col2:
    cpu_usage = system_monitor.get_cpu_usage()
    st.metric("CPU Usage", f"{cpu_usage}%")

with col3:
    memory_usage = system_monitor.get_memory_usage()
    st.metric("Memory Usage", f"{memory_usage}%")

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
log_container = st.empty()

# Create an expandable container for logs
with st.expander("View Logs", expanded=True):
    log_text = "\n".join(log_output)
    st.code(log_text, language="plain")

# Auto-refresh every 5 seconds
time.sleep(5)
st.experimental_rerun()
