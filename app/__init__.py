#!/usr/bin/python3
# app/__init__.py

import os
from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask_bootstrap import Bootstrap

from app.config import app_config
import importlib

#app = Flask(__name__, template_folder='templates', instance_relative_config=True)

print(u"Current path is", os.path.abspath(os.curdir), sep=' ')


def create_app(config_name, version):
    """
    This is the method that initializes modules used in the app
    :param config_name: The key for the configuration to use
    :return: Flask app
    """
    if config_name not in app_config.keys():
        config_name = 'development'

    app = importlib.import_module('app.' + version).app
    app.config.from_object(".".join(["app", "config", app_config[config_name]]))
    # use if you have instance/config.py with your SECRET_KEY and SQLALCHEMY_DATABASE_URI
    app.config.from_pyfile('instance/config.py')

    return app