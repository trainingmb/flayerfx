#!/usr/bin/python3
"""
Contains class BaseModel
"""

from datetime import datetime
import models
from os import getenv
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import uuid
import dateutil.parser

time = "%Y-%m-%dT%H:%M:%S.%f"

if 'db' in models.storage_t:
    Base = declarative_base()
else:
    Base = object

class BaseModel:
    """The BaseModel class from which future classes will be derived"""
    if 'db' in models.storage_t:
        id = Column(String(60), primary_key=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Initialization of the base model"""
        if args != []:
            for i, j in args:
                kwargs[i] = j
        if kwargs:
            for key, value in kwargs.items():
                if key != "__class__":
                    if key[-3:] == '_at' and type(value) is str:
                        try:
                            setattr(self, key, dateutil.parser.parse(value))
                        except ValueError:
                            setattr(self, key, value)
                        except dateutil.parser._parser.ParserError:
                            setattr(self, key, value)
                    else:
                        setattr(self, key, value)
            if kwargs.get("created_at", None) and type(self.created_at) is str:
                self.created_at = datetime.strptime(kwargs["created_at"], time)
            else:
                self.created_at = datetime.utcnow()
            if kwargs.get("updated_at", None) and type(self.updated_at) is str:
                self.updated_at = datetime.strptime(kwargs["updated_at"], time)
            elif type(kwargs.get("updated_at", None)) is datetime:
                self.updated_at = kwargs.get("updated_at", None)
            else:
                self.updated_at = datetime.utcnow()
            if kwargs.get("id", None) is None:
                self.id = str(uuid.uuid4())
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.utcnow()
            self.updated_at = self.created_at

    def __str__(self):
        """String representation of the BaseModel class"""
        return "[{:s}] ({:s}) {}".format(self.__class__.__name__, self.id,
                                         self.__dict__)

    def save(self):
        """updates the attribute 'updated_at' with the current datetime"""
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self, save_fs=None):
        """returns a dictionary containing all keys/values of the instance"""
        new_dict = self.__dict__.copy()
        if "created_at" in new_dict:
            new_dict["created_at"] = new_dict["created_at"].strftime(time)
        if "updated_at" in new_dict:
            new_dict["updated_at"] = new_dict["updated_at"].strftime(time)
        new_dict["__class__"] = self.__class__.__name__
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
        if save_fs is None:
            if "password" in new_dict:
                del new_dict["password"]
        for key, value in new_dict.items():
            if key[-3:] == '_at' and type(value) is datetime:
                new_dict[key] = new_dict[key].strftime(time)
        return new_dict

    def delete(self):
        """delete the current instance from the storage"""
        models.storage.delete(self)
