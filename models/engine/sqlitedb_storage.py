#!/usr/bin/python3
"""
Contains the class SQLiteDBStorage
"""
from models.engine.db_storage import Base, create_engine, DBStorage, path

class SQLiteDBStorage(DBStorage):
    """interacts with the SQLite database"""
    __file_path = "file.db"

    def __init__(self):
        """Instantiate a DBStorage object"""
        if not path.exists(self.__file_path):
            with open(self.__file_path, 'w'): pass

        self.__engine = create_engine(f'sqlite:///{self.__file_path}')
        Base.metadata.bind = self.__engine
        super().__init__(self.__engine)