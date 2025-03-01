import logging
from collections import deque
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create a thread-safe circular buffer for logs
log_buffer = deque(maxlen=100)
log_lock = threading.Lock()

class BufferHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        with log_lock:
            log_buffer.append(log_entry)

# Add buffer handler to logger
buffer_handler = BufferHandler()
buffer_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(buffer_handler)

def get_recent_logs():
    """Get recent log entries from the buffer"""
    with log_lock:
        return list(log_buffer)
