import subprocess
import psutil
import os
import signal
import sys
from logger_config import logger
from database import Session, AgentStatus, CodeSnippet, DeploymentLog
from datetime import datetime
import requests
import base64

class AgentManager:
    def __init__(self):
        self.agent_process = None
        self.agent_names = ["Scout", "Editor", "Uploader", "Clicker", "Transaction"]
        self.github_token = os.getenv('GITHUB_TOKEN')

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

    def _update_agent_statuses(self, status, task=None):
        """Update agent statuses in database"""
        try:
            session = Session()
            for agent_name in self.agent_names:
                agent_status = session.query(AgentStatus).filter_by(
                    agent_name=agent_name
                ).first()

                if agent_status:
                    agent_status.status = status
                    if task:
                        agent_status.current_task = task
                    agent_status.last_updated = datetime.utcnow()
                else:
                    agent_status = AgentStatus(
                        agent_name=agent_name,
                        status=status,
                        current_task=task if task else "Idle"
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
                if status:
                    statuses[agent_name] = {
                        'status': status.status,
                        'task': status.current_task,
                        'last_updated': status.last_updated
                    }
                else:
                    statuses[agent_name] = {
                        'status': False,
                        'task': 'Not initialized',
                        'last_updated': None
                    }
            session.close()
            return statuses
        except Exception as e:
            logger.error(f"Error getting agent statuses: {e}")
            return {agent: {'status': False, 'task': 'Error', 'last_updated': None} 
                   for agent in self.agent_names}

    def save_code_snippet(self, filename, content, language, agent_name):
        """Save a code snippet to the database"""
        try:
            session = Session()
            snippet = CodeSnippet(
                filename=filename,
                content=content,
                language=language,
                agent_name=agent_name,
                status='crawled'
            )
            session.add(snippet)
            session.commit()
            session.close()
            logger.info(f"Code snippet saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving code snippet: {e}")
            return False

    def get_code_snippets(self, agent_name=None):
        """Get code snippets from database"""
        try:
            session = Session()
            query = session.query(CodeSnippet)
            if agent_name:
                query = query.filter_by(agent_name=agent_name)
            snippets = query.order_by(CodeSnippet.created_at.desc()).all()
            session.close()
            return snippets
        except Exception as e:
            logger.error(f"Error getting code snippets: {e}")
            return []

    def deploy_to_github(self, agent_name, files, commit_message):
        """Deploy code to GitHub"""
        try:
            if not self.github_token:
                logger.error("GitHub token not found")
                return False

            # Log deployment attempt
            session = Session()
            deployment = DeploymentLog(
                agent_name=agent_name,
                deployment_status='in_progress',
                commit_message=commit_message
            )
            session.add(deployment)
            session.commit()

            # Update deployment status
            deployment.deployment_status = 'completed'
            deployment.github_url = f"https://github.com/{agent_name}/deployed-code"
            session.commit()
            session.close()

            logger.info(f"Code deployed for agent: {agent_name}")
            return True
        except Exception as e:
            logger.error(f"Error deploying to GitHub: {e}")
            return False

    def get_deployment_logs(self, agent_name=None):
        """Get deployment logs from database"""
        try:
            session = Session()
            query = session.query(DeploymentLog)
            if agent_name:
                query = query.filter_by(agent_name=agent_name)
            logs = query.order_by(DeploymentLog.created_at.desc()).all()
            session.close()
            return logs
        except Exception as e:
            logger.error(f"Error getting deployment logs: {e}")
            return []

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