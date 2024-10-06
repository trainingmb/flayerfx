#!/usr/bin/python3
"""
Initialize Logger Package
"""
from logger.base_logger import BaseLogger

logHandler = None

def init_logger(app):
	global logHandler
	logHandler = BaseLogger(app, 'flayerfx')
