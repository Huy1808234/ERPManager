import logging
import os
import sys

# Define AppData directory for the application
APP_NAME = "VLXD_ThongNhat"

if sys.platform == "win32":
    APP_DATA_DIR = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME)
else:
    APP_DATA_DIR = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")

LOG_DIR = os.path.join(APP_DATA_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure logger
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

# Create handlers
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
console_handler.setFormatter(log_format)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def get_logger():
    return logger
