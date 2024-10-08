#!/usr/bin/python3
"""
Initialize Logger Package
"""
from logger.base_logger import BaseLogger
from logging.config import dictConfig


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s | %(module)s >>> %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
)

logHandler = None
def init_logger(app):
	global logHandler
	logHandler = BaseLogger(app, 'flayerfx')
