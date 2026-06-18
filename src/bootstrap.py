"""Bootstrap script for initializing the basic services.
"""

# Standard library imports
import dotenv
import logging
from logging.config import dictConfig
import os


# Module initialization
dotenv.load_dotenv()  # Load environment variables from .env file
LOG_DIR = os.getenv('LOG_DIR', 'logs')  # Default to 'logs' if not set

_DEFAULT_UBER_RAW_DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')
UBER_RAW_DATA_URL = os.getenv("UBER_RAW_DATA_URL", _DEFAULT_UBER_RAW_DATA_URL)
UBER_RAW_DATA_DATE_COLUMN = os.getenv("UBER_RAW_DATA_DATE_COLUMN", "date/time")

# Define your centralized logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "ecs": {
            "()": "ecs_logging.StdlibFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file_handler": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": f"{LOG_DIR}/app.log",
            "mode": "a",
            "encoding": "utf-8",
        },
        "ecs_file": {
            "class": "logging.FileHandler",
            "filename": f"{LOG_DIR}/app-ecs.json",
            "formatter": "ecs",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "file_handler", "ecs_file"],
        "level": "INFO",
    },
}

class ServiceContainer:
    """Container of basic services"""
    def __init__(self, service_name: str):
        self.service_name = service_name
        
        os.makedirs(LOG_DIR, exist_ok=True)
        dictConfig(LOGGING_CONFIG)
        self.root_logger = logging.getLogger(self.service_name)
        
    def __enter__(self):
        self.root_logger.info(f"Bootstrapping application for service: {self.service_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.root_logger.info(f"Shutting down application for service: {self.service_name}")
