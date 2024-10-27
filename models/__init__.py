#!/usr/bin/python3
"""
This module initializes the storage engine for the application based on the 
environment variable `FLAYERFX_TYPE_STORAGE`. It supports MySQL, JSON file, 
and SQLite storage types.
Module:
    - storage: An instance of the selected storage engine.
Usage:
    Set the `FLAYERFX_TYPE_STORAGE` environment variable to one of the 
    following values to select the storage engine:
        - "db_mysql": Use MySQLDBStorage.
        - "json": Use FileStorage.
        - Any other value or unset: Use SQLiteDBStorage.
    Example:
        export FLAYERFX_TYPE_STORAGE=db_mysql
        python your_script.py
"""

from os import getenv, environ

storage_t = getenv("FLAYERFX_TYPE_STORAGE")
if storage_t == "db_mysql":
    from models.engine.mysqldb_storage import MySQLDBStorage
    print("Working ON MySQLDB Storage")
    storage = MySQLDBStorage()
elif storage_t == "json":
    storage_t = "file_json"
    from models.engine.file_storage import FileStorage
    print("Working ON File Storage")
    storage = FileStorage()
else:
    storage_t = "db_sqllite"
    from models.engine.sqlitedb_storage import SQLiteDBStorage
    print("Working ON SQLiteDB Storage")
    storage = SQLiteDBStorage()
storage.reload()