#!/usr/bin/python3
"""
Contains the class DBStorage
"""

import models
from models.base_model import BaseModel, Base
from models.store import Store
from models.product import Product
from models.price import Price
from os import getenv, path
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

classes = {"Store": Store, "Product": Product,
          "Price": Price}
class_tables = {"Store": [ Store.name ],
          "Product": [ Product.store_id, Product.name, Product.link ],
          "Price": [ Price.product_id, Price.amount, Price.is_discount ]}


class DBStorage:
    """interacts with the database"""
    __engine = None
    __session = None

    def __init__(self, engine=None):
        """Instantiate a DBStorage object"""
        self.__engine = engine
        FLAYERFX_ENV = getenv('FLAYERFX_ENV')
        if FLAYERFX_ENV == "test":
            Base.metadata.drop_all(self.__engine)

    def all_select(self, cls, tables=[]):
        """query on the current database session"""
        new_dict = {}
        for clss in classes:
            if cls is classes[clss] or cls is clss:
                tb=[]
                for i in tables:
                    if i in class_tables[clss]:
                        tb.append(i)
                if len(tb) > 0:
                    if classes[clss].id not in tb:
                        tb.append(classes[clss].id)
                    objs = self.__session.query(*tb).all()
                    for obj in objs:
                        key = obj.__class__.__name__ + '.' + obj.id
                        new_dict[key] = obj
        return (new_dict)

    def all(self, cls=None):
        """query on the current database session"""
        new_dict = {}
        for clss in classes:
            if cls is None or cls is classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss]).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        return (new_dict)

    def new(self, obj):
        """add the object to the current database session"""
        if type(obj) == list:
            self.__session.add_all(obj)
        else:
            self.__session.add(obj)

    def save(self):
        """commit all changes of the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """delete from the current database session obj if not None"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """reloads data from the database"""
        print("Engine = ", self.__engine)
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

    def close(self):
        """call remove() method on the private session attribute"""
        self.__session.remove()

    def get(self, cls, **kwargs):
        """
        Returns the object based on the class name and its ID, or
        None if not found
        """
        if cls not in classes.values():
            return None
        filtered_cls = self.__session.query(cls).filter_by(**kwargs).all()
        if (len(filtered_cls) < 1):
            return None
        return filtered_cls

    def count(self, cls=None):
        """
        count the number of objects in storage
        """
        all_class = classes.values()

        if not cls:
            count = 0
            for clas in all_class:
                count += len(models.storage.all(clas).values())
        else:
            count = len(models.storage.all(cls).values())

        return count