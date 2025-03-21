import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs in 'logger/logs'
current_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(current_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Define log file path with timestamp
log_date = datetime.now().strftime("%Y-%m-%d")
log_file_path = os.path.join(logs_dir, f"adventure_ai_{log_date}.log")

# Configure the root logger with base settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create and configure a file handler for all loggers
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# Create console handler for all loggers
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)


# Define logger creation function
def get_logger(name, level=logging.INFO):
    """
    Create and return a logger with the specified name and level.

    Args:
        name (str): The name of the logger, typically the module name
        level (int): The logging level (default: logging.INFO)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if handlers already added to avoid duplicates
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Pre-configured loggers for different components
db_logger = get_logger("app.database")
api_logger = get_logger("app.api")
game_logger = get_logger("app.game")
auth_logger = get_logger("app.auth")
general_logger = get_logger("app.general")
