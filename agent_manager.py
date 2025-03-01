import subprocess
import psutil
import os
import signal
from logger_config import logger

class AgentManager:
    def __init__(self):
        self.agent_process = None
        self.agent_names = ["Scout", "Editor", "Uploader", "Clicker", "Transaction"]
        
    def start_agents(self):
        """Start the AI agents"""
        try:
            if not self.is_running():
                script_path = os.path.join(os.path.dirname(__file__), 'main.py')
                self.agent_process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                logger.info("Agents started successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to start agents: {e}")
            return False

    def stop_agents(self):
        """Stop the AI agents"""
        try:
            if self.agent_process:
                self.agent_process.terminate()
                self.agent_process.wait(timeout=5)
                self.agent_process = None
                logger.info("Agents stopped successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to stop agents: {e}")
            return False

    def is_running(self):
        """Check if agents are running"""
        if self.agent_process:
            return self.agent_process.poll() is None
        return False

    def get_agent_statuses(self):
        """Get status of all agents"""
        is_running = self.is_running()
        return {agent: is_running for agent in self.agent_names}
