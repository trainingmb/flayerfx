#!/usr/bin/python3
"""
Module: base_model
This module contains the definition of the BaseModel class, which serves as the 
base class for all future classes in the application. It provides common 
attributes and methods that will be inherited by other models.
Classes:
    BaseModel: A base class for all models, providing common attributes and methods.
Usage:
    class MyModel(BaseModel):
        pass
    instance = MyModel()
    instance.save()
    print(instance)
    instance_dict = instance.to_dict()
    instance.delete()
"""

from datetime import datetime
import uuid
import dateutil.parser
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

from models import storage_t

time = "%Y-%m-%dT%H:%M:%S.%f"

if 'db' in storage_t:
    Base = declarative_base()
else:
    Base = object

class BaseModel:
    """
    BaseModel class
    The BaseModel class serves as the base class for all future classes in the application. It provides common attributes and methods that will be inherited by other models.
    Attributes:
        id (str): The unique identifier for each instance.
        created_at (datetime): The timestamp when the instance was created.
        updated_at (datetime): The timestamp when the instance was last updated.
    Methods:
        __init__(*args, **kwargs): Initializes a new instance of BaseModel.
        __str__(): Returns a string representation of the BaseModel instance.
        __repr__(): Returns a string representation of the BaseModel instance.
        save(): Updates the 'updated_at' attribute with the current datetime and saves the instance to storage.
        to_dict(save_fs=None): Returns a dictionary containing all keys/values of the instance.
        delete(): Deletes the current instance from the storage.
    """
    if 'db' in storage_t:
        id = Column(String(60), primary_key=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """
        Initializes an instance of the base model.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Keyword Args:
            created_at (str or datetime, optional): The creation timestamp.
            updated_at (str or datetime, optional): The last updated timestamp.
            *_at (str or datetime, optional): Any other timestamp attribute.
            id (str, optional): The unique identifier for the instance.
            Other attributes can be passed as keyword arguments.

        Notes:
            - If `created_at` or `updated_at` are provided as strings, they will be parsed into datetime objects.
            - If `id` is not provided, a new UUID will be generated.
            - If `created_at` or `updated_at` are not provided, the current UTC time will be used.
        """
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
        """
        Returns a string representation of the BaseModel instance.

        The string representation includes the class name, the instance ID, 
        and a dictionary of the instance's attributes.

        Returns:
            str: A formatted string representing the BaseModel instance.
        """
        return "[{:s}] ({:s}) {}".format(self.__class__.__name__, self.id,
                                         self.__dict__)

    def save(self):
        """
        Saves the current instance to the storage.

        This method updates the 'updated_at' attribute with the current UTC datetime,
        adds the instance to the storage, and then saves the storage.

        Raises:
            Exception: If there is an issue with saving the instance to the storage.
        """
        from models import storage
        self.updated_at = datetime.utcnow()
        storage.save()

    def to_dict(self, save_fs=None):
        """
        Converts the instance attributes to a dictionary.

        Args:
            save_fs (bool, optional): If None, the 'password' key will be removed from the dictionary.

        Returns:
            dict: A dictionary representation of the instance, with datetime attributes formatted as strings.
        """
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
        """
        Deletes the current instance from the storage.

        This method removes the instance from the storage system managed by the
        `models.storage` object.
        """
        from models import storage
        storage.delete(self)

    def __repr__(self):
        """
        Returns a string representation of the BaseModel instance.

        The string representation includes the class name, the instance ID, 
        and a dictionary of the instance's attributes.

        Returns:
            str: A formatted string representing the BaseModel instance.
        """
        return self.__str__()
    
