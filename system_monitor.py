import psutil
import subprocess
import time
from logger_config import logger

class SystemMonitor:
    def check_ollama_status(self):
        """Check if Ollama is running"""
        try:
            for proc in psutil.process_iter(['name']):
                if 'ollama' in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking Ollama status: {e}")
            return False

    def get_cpu_usage(self):
        """Get current CPU usage"""
        try:
            return round(psutil.cpu_percent(interval=1), 2)
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return 0.0

    def get_memory_usage(self):
        """Get current memory usage"""
        try:
            return round(psutil.virtual_memory().percent, 2)
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0.0

    def restart_ollama(self):
        """Restart Ollama service"""
        try:
            subprocess.run(["ollama", "stop"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            time.sleep(2)
            subprocess.run(["ollama", "start"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            logger.info("Ollama restarted successfully")
            return True
        except Exception as e:
            logger.error(f"Error restarting Ollama: {e}")
            return False
