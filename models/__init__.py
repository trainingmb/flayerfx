#!/usr/bin/python3
"""
Initialize Models Package
"""

from os import getenv, environ

storage_t = getenv("FLAYERFX_TYPE_STORAGE")
print(environ)
if storage_t == "db_mysql":
    from models.engine.mysqldb_storage import MySQLDBStorage
    print("Working ON MySQLDB Storage")
    storage = MySQLDBStorage()
elif storage_t == "db_sqlite":
    from models.engine.sqlitedb_storage import SQLiteDBStorage
    print("Working ON SQLiteDB Storage")
    storage = SQLiteDBStorage()
else:
    storage_t = "file_json"
    from models.engine.file_storage import FileStorage
    print("Working ON File Storage")
    storage = FileStorage()
storage.reload()
