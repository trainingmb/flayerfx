#!/usr/bin/python3
"""
Module: sqlitedb_storage
This module defines the SQLiteDBStorage class for interacting with an SQLite database.
Classes:
    SQLiteDBStorage: A class representing the storage engine for SQLite databases.
Public Functions:
    __init__(): Initializes a new instance of the SQLiteDBStorage class.
Usage:
    This module is used to create and manage an SQLite database connection using SQLAlchemy.
    Example:
        storage = SQLiteDBStorage()
        # Now you can use `storage` to interact with the SQLite database.
"""
from os import path

from sqlalchemy import create_engine

from models.engine.db_storage import Base, DBStorage

class SQLiteDBStorage(DBStorage):
    """
    SQLiteDBStorage is a class that interacts with the SQLite database.
    Attributes:
        __file_path (str): The path to the SQLite database file.
        __engine (Engine): The SQLAlchemy engine connected to the SQLite database.
    Methods:
        __init__(): Initializes a new instance of the SQLiteDBStorage class. 
                    If the database file does not exist, it creates an empty file.
    """
    __file_path = "file.db"

    def __init__(self):
        """Instantiate a DBStorage object"""
        if not path.exists(self.__file_path):
            with open(self.__file_path, 'w'): pass

        self.__engine = create_engine(f'sqlite:///{self.__file_path}')
        Base.metadata.bind = self.__engine
        super().__init__(self.__engine)