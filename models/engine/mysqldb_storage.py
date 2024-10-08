#!/usr/bin/python3
"""
Contains the class MySQLDBStorage
"""
from sqlalchemy import create_engine
from models.engine.db_storage import Base, DBStorage, getenv 

class MySQLDBStorage(DBStorage):
    """interacts with the MYSQL database"""

    def __init__(self):
        """Instantiate a DBStorage object"""
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