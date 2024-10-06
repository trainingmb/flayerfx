#!/usr/bin/python3
# flayer/__init__.py

import os

from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask_bootstrap import Bootstrap

from app.config import app_config
from logger import init_logger
import importlib



def create_app(config_name, version):
    """
    This is the method that initializes modules used in the app
    :param config_name: The key for the configuration to use
    :return: Flask app
    """

    if config_name not in app_config.keys():
        config_name = 'development'
    app = Flask(__name__, template_folder=f'app/{version}/templates', static_folder=f'app/{version}/static')
    init_logger(app)
    api_views = importlib.import_module(f'api.{version}.views').api_views
    app_views = importlib.import_module(f'app.{version}.views').app_views
    app.config.from_object(".".join(["app", "config", app_config[config_name]]))
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.register_blueprint(api_views)
    app.register_blueprint(app_views)
    app.config['CORS_HEADERS'] = 'Content-Type'
    # use if you have instance/config.py with your SECRET_KEY and SQLALCHEMY_DATABASE_URI
    app.config.from_pyfile(f'app/{version}/instance/config.py')

    return app
