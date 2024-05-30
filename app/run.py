#!/usr/bin/python3

import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
if not config_name:
    config_name = 'development'
app = create_app(config_name, 'v1')

if __name__ == '__main__':
    app.run()