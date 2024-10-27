#!/usr/bin/python3
"""
Module: file_storage
This module defines the FileStorage class for serializing and deserializing
instances to and from a JSON file.
Classes:
    FileStorage: A class responsible for storing and retrieving objects
    from a JSON file.
Public Functions:
    all(cls=None): Returns the dictionary __objects.
    new(obj): Sets in __objects the obj with key <obj class name>.id.
    save(): Serializes __objects to the JSON file (path: __file_path).
    reload(): Deserializes the JSON file to __objects.
    delete(obj=None): Deletes obj from __objects if it’s inside.
    close(): Calls reload() method for deserializing the JSON file to objects.
    get(cls, **kwargs): Returns the object based on the class name and its ID, or None if not found.
    count(cls=None): Counts the number of objects in storage.
    search(cls, **kwargs): Searches for an object in the database by kwargs.
Usage:
    This module is used to manage the storage of objects in a JSON file,
    allowing for serialization and deserialization of objects.
    Example:
        storage = FileStorage()
        storage.reload()
        all_objects = storage.all()
        storage.new(obj)
        storage.save()
        storage.delete(obj)
        result = storage.get(Store, id="123")
        count = storage.count(Product)
        search_results = storage.search(Product, name="example")
"""

import json
from hashlib import md5

from models.class_store import classes
from models.engine.matchscore import match_score, SCORETHRESHOLD



class FileStorage:
    """
    FileStorage class for serializing instances to a JSON file and deserializing back to instances.
    Attributes:
        __file_path (str): Path to the JSON file.
        __objects (dict): Dictionary to store all objects by <class name>.id.
    Methods:
        all(cls=None):
            Returns the dictionary __objects. If cls is provided, returns a dictionary of objects of that class.
        new(obj):
            Sets in __objects the obj with key <obj class name>.id. If obj is a list, sets each item in the list.
        save():
            Serializes __objects to the JSON file (path: __file_path).
        reload():
            Deserializes the JSON file to __objects.
        delete(obj=None):
            Deletes obj from __objects if it’s inside.
        close():
            Calls reload() method for deserializing the JSON file to objects.
        get(cls, **kwargs):
            Returns the object based on the class name and its ID, or None if not found.
        count(cls=None):
            Counts the number of objects in storage. If cls is provided, counts the number of objects of that class.
        search(cls, **kwargs):
            Searches for an object in the database by kwargs. Returns a list of objects that match the search criteria.
    """
    # string - path to the JSON file
    __file_path = "file.json"
    # dictionary - empty but will store all objects by <class name>.id
    __objects = {}

    def all(self, cls=None):
        """
        Returns a dictionary of objects currently stored.

        If a class is provided, only objects of that class or objects whose class name matches
        the provided class name will be included in the returned dictionary.

        Args:
            cls (type or str, optional): The class or class name to filter objects by.

        Returns:
            dict: A dictionary of objects, filtered by the provided class if specified.
        """
        if cls is not None:
            new_dict = {}
            for key, value in self.__objects.items():
                if cls == value.__class__ or cls == value.__class__.__name__:
                    new_dict[key] = value
            return new_dict
        return self.__objects

    def new(self, obj):
        """
        Adds a new object or a list of objects to the storage.

        If the input is a list of objects, each object is added to the storage
        with a key in the format <obj class name>.<obj id>. If the input is a 
        single object, it is added to the storage with a key in the same format.

        Args:
            obj (object or list): The object or list of objects to be added to the storage.
        """
        if type(obj) == list:
            for i in obj:
                key = i.__class__.__name__ + "." + i.id
                self.__objects[key] = i
        elif obj is not None:
            key = obj.__class__.__name__ + "." + obj.id
            self.__objects[key] = obj

    def save(self):
        """
        Serializes the __objects attribute to a JSON file specified by __file_path.

        This method converts the __objects attribute to a dictionary of JSON-serializable
        objects and writes it to a file in JSON format. If an object's key is "password",
        it decodes the value before serialization.

        Raises:
            IOError: If the file cannot be opened or written to.
        """
        json_objects = {}
        for key in self.__objects:
            if key == "password":
                json_objects[key].decode()
            json_objects[key] = self.__objects[key].to_dict(save_fs=1)
        with open(self.__file_path, 'w') as f:
            json.dump(json_objects, f)

    def reload(self):
        """
        Deserializes the JSON file to __objects.

        This method attempts to open a JSON file specified by the instance's
        __file_path attribute. If the file is successfully opened and read,
        it loads the JSON content into a dictionary. Each key-value pair in
        the dictionary is then used to instantiate objects of the appropriate
        class, as specified by the "__class__" attribute in the JSON data.
        These objects are stored in the instance's __objects attribute.

        If any exception occurs during this process (e.g., the file does not
        exist, the JSON is malformed, or the class cannot be found), the
        exception is silently ignored and the method exits without making
        any changes to __objects.
        """
        try:
            with open(self.__file_path, 'r') as f:
                jo = json.load(f)
            for key in jo:
                self.__objects[key] = classes[jo[key]["__class__"]](**jo[key])
        except:
            pass

    def delete(self, obj=None):
        """
        Delete an object from the storage.

        Args:
            obj: The object to be deleted. If obj is None, the method does nothing.

        Deletes the object from the internal storage dictionary if it exists.
        The key for the object is generated using the class name and the object's id.
        """
        if obj is not None:
            key = obj.__class__.__name__ + '.' + obj.id
            if key in self.__objects:
                del self.__objects[key]

    def close(self):
        """
        Closes the storage by calling the reload method to deserialize the JSON file into objects.
        """
        self.reload()

    def rollback(self):
        """
        Rollback the storage to the last saved state.
        """
        self.reload()

    def get(self, cls, **kwargs):
        """
        Retrieves objects of a specified class that match given attribute values.
        Args:
            cls (type): The class type of the objects to retrieve.
            **kwargs: Arbitrary keyword arguments representing the attribute names 
                      and their corresponding values to filter the objects.
        Returns:
            list: A list of objects that match the specified class and attribute values.
                  Returns None if the class is not found or no matching objects are found.
        """        
        if cls not in classes.values():
            return None

        all_cls = self.all(cls)
        filtered_results = []
        for value in all_cls.values():
            obj_flag = False
            for key, v in kwargs.items():
                try:
                    x = getattr(value, key, None)
                    if x is not None and x == v:
                        obj_flag=True
                    else:
                        obj_flag=False
                except Exception:
                    obj_flag=False
                if obj_flag == False:
                    break
            if obj_flag == True:
                filtered_results.append(value)
        if (len(filtered_results) < 1):
            return None
        return filtered_results 

    def count(self, cls=None):
        #TODO: This can be done better without using all
        """
        Count the number of objects in storage.
        Args:
            cls (type, optional): The class type to count instances of. If None, count instances of all classes.
        Returns:
            int: The number of objects in storage.
        """
        all_class = classes.values()

        if not cls:
            count = 0
            for clas in all_class:
                count += len(self.all(clas))
        else:
            count = len(self.all(cls))

        return count

    def search(self, cls, **kwargs):
        """
        Search for an object in the database by specified keyword arguments.
        Args:
            cls (type): The class type of the objects to search for.
            **kwargs: Arbitrary keyword arguments to filter the objects.
        Returns:
            list: A list of objects that match the search criteria, sorted by match score.
                  Returns None if no objects match the criteria.
        Raises:
            Exception: If an error occurs while accessing object attributes.
        """        
        if cls not in classes.values():
            return None

        all_cls = self.all(cls)
        filtered_results = []
        for value in all_cls.values():
            score = 0
            for key, v in kwargs.items():
                try:
                    x = getattr(value, key, None)
                    if x is not None and x == v:
                        obj_flag=True
                    else:
                        obj_flag=False
                except Exception:
                    obj_flag=False
                if obj_flag == False:
                    break
            score = match_score(kwargs['name'], value.name)
            if score >= SCORETHRESHOLD:
                filtered_results.append((score, value))
        if (len(filtered_results) < 1):
            return None
        return [i[1] for i in sorted(filtered_results, key=lambda a: a[0])]
    
    def get_deals(self, dateleft, dateright):
        """
        Get deals between two dates.

        This method retrieves the first Price record for each product where the 
        fetched_at date is between the specified dateleft and dateright, and the 
        discount is True.

        Args:
            dateleft (datetime): The start date for filtering deals.
            dateright (datetime): The end date for filtering deals.

        Returns:
            list: A list of Price objects that match the criteria.
        """
        from models.price import Price
        #Mapping product_id to Price
        deals = {}
        for price in self.all(Price).values():
            if price.fetched_at >= dateleft and price.fetched_at <= dateright and price.is_discount:
                if price.product_id not in deals:
                    deals[price.product_id] = price
                else:
                    if price.fetched_at > deals[price.product_id].fetched_at:
                        deals[price.product_id] = price
        return list(deals.values())