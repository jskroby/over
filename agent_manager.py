import subprocess
import psutil
import os
import signal
import sys
from logger_config import logger
from database import Session, AgentStatus, WorkspaceFolder
from datetime import datetime

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
                self._update_agent_statuses(True)
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
                self._update_agent_statuses(False)
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

    def _update_agent_statuses(self, status):
        """Update agent statuses in database"""
        try:
            session = Session()
            for agent_name in self.agent_names:
                agent_status = session.query(AgentStatus).filter_by(
                    agent_name=agent_name
                ).first()

                if agent_status:
                    agent_status.status = status
                    agent_status.last_updated = datetime.utcnow()
                else:
                    agent_status = AgentStatus(
                        agent_name=agent_name,
                        status=status
                    )
                    session.add(agent_status)

            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Error updating agent statuses: {e}")

    def get_agent_statuses(self):
        """Get status of all agents from database"""
        try:
            session = Session()
            statuses = {}
            for agent_name in self.agent_names:
                status = session.query(AgentStatus).filter_by(
                    agent_name=agent_name
                ).first()
                statuses[agent_name] = status.status if status else False
            session.close()
            return statuses
        except Exception as e:
            logger.error(f"Error getting agent statuses: {e}")
            return {agent: False for agent in self.agent_names}

    def create_folder(self, folder_name):
        """Create a new folder in the workspace"""
        try:
            folder_path = os.path.join(os.getcwd(), folder_name)
            os.makedirs(folder_path, exist_ok=True)

            session = Session()
            workspace_folder = WorkspaceFolder(folder_name=folder_name)
            session.add(workspace_folder)
            session.commit()
            session.close()

            logger.info(f"Created folder: {folder_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return False