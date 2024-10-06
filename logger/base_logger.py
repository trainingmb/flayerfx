#!/usr/bin/python3
"""
Base Logger
"""

import logging
from flask import Flask

class BaseLogger:
    def __init__(self, app: Flask = None, name: str = 'base_logger', level: int = logging.INFO):
        if app:
            self.logger = app.logger
        else:
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)
            self._setup_handler()

    def _setup_handler(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)