#!/usr/bin/python3
"""
Module: mysqldb_storage
This module defines the MySQLDBStorage class for interacting with a MySQL database.
Classes:
    MySQLDBStorage: A class representing the storage engine for MySQL databases.
Public Functions:
    __init__(): Initializes a new instance of MySQLDBStorage, setting up the database connection.
Usage:
    This module is used to create a connection to a MySQL database and interact with it using SQLAlchemy.
    Example:
        storage = MySQLDBStorage()
"""
from os import getenv

from sqlalchemy import create_engine

from models.engine.db_storage import Base, DBStorage 

class MySQLDBStorage(DBStorage):
    """
    MySQLDBStorage is a class that interacts with the MySQL database.
    Attributes:
        __engine (sqlalchemy.engine.Engine): SQLAlchemy engine instance for MySQL database connection.
    Methods:
        __init__(): Initializes a MySQLDBStorage instance, sets up the database engine, and binds the metadata.
    """

    def __init__(self):
        """
        Initialize a DBStorage object.

        This method sets up the database connection using environment variables
        for the MySQL user, password, host, and database name. It creates an
        SQLAlchemy engine with connection pooling and binds the engine to the
        metadata of the Base class.

        Environment Variables:
            FLAYERFX_MYSQL_USER: MySQL username.
            FLAYERFX_MYSQL_PWD: MySQL password.
            FLAYERFX_MYSQL_HOST: MySQL host.
            FLAYERFX_MYSQL_DB: MySQL database name.
        """
        FLAYERFX_MYSQL_USER = getenv('FLAYERFX_MYSQL_USER')
        FLAYERFX_MYSQL_PWD = getenv('FLAYERFX_MYSQL_PWD')
        FLAYERFX_MYSQL_HOST = getenv('FLAYERFX_MYSQL_HOST')
        FLAYERFX_MYSQL_DB = getenv('FLAYERFX_MYSQL_DB')
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.
                                      format(FLAYERFX_MYSQL_USER,
                                             FLAYERFX_MYSQL_PWD,
                                             FLAYERFX_MYSQL_HOST,
                                             FLAYERFX_MYSQL_DB),
                                      pool_recycle=3600,
                                      pool_pre_ping=True)
        Base.metadata.bind = self.__engine
        super().__init__(self.__engine)