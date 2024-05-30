#!/usr/bin/bash
pip install flask flask_cors sqlalchemy mysqlclient python-dateutil flask-wtf flasgger
export TZ="Asia/Istanbul"
export FLAYERFX_MYSQL_USER=flayerfx
export FLAYERFX_MYSQL_HOST=flayerfx.mysql.pythonanywhere-services.com
export FLAYERFX_MYSQL_DB="flayerfx$scrap"
export FLAYERFX_ENV="dev"
export FLAYERFX_TYPE_STORAGE=db
