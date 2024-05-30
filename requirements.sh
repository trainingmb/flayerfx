#!/usr/bin/bash
pip install flask flask_cors sqlalchemy mysqlclient python-dateutil flask-wft
export TZ="Asia/Istanbul"
export INADIS_MYSQL_USER=stofgenius
export INADIS_MYSQL_HOST=stofgenius.mysql.pythonanywhere-services.com
export INADIS_MYSQL_DB="stofgenius$stories"
export INADIS_ENV="dev"
export INADIS_TYPE_STORAGE=db