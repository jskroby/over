import logging
from datetime import datetime

class AgentInteraction:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.logger = logging.getLogger(__name__)

    def format_message(self, message, to="user"):
        """Format message in the conversation style from the logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.agent_name} (to {to}):\n\n{message}\n\nTERMINATE\n\n{'-'*80}"

    def send_message(self, message):
        """Send a message and format it according to the log style"""
        try:
            formatted_msg = self.format_message(message)
            self.logger.info(formatted_msg)
            return formatted_msg
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return None

    def code_block(self, code, filename=None):
        """Format code blocks as shown in the logs"""
        header = f"# filename: {filename}\n" if filename else ""
        return f"```python\n{header}{code}\n```"