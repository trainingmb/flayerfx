#!/usr/bin/python3
"""
Contains the FileStorage class
"""

import json
import models
from models.store import Store
from models.product import Product
from models.price import Price
from hashlib import md5

classes = {"Store": Store, "Product": Product,
          "Price": Price}


class FileStorage:
    """serializes instances to a JSON file & deserializes back to instances"""

    # Threshold score for filtering search results
    SCORETHRESHOLD = 70

    # string - path to the JSON file
    __file_path = "file.json"
    # dictionary - empty but will store all objects by <class name>.id
    __objects = {}

    def all(self, cls=None):
        """returns the dictionary __objects"""
        if cls is not None:
            new_dict = {}
            for key, value in self.__objects.items():
                if cls == value.__class__ or cls == value.__class__.__name__:
                    new_dict[key] = value
            return new_dict
        return self.__objects

    def new(self, obj):
        """sets in __objects the obj with key <obj class name>.id"""
        if type(obj) == list:
            for i in obj:
                key = i.__class__.__name__ + "." + i.id
                self.__objects[key] = i
        elif obj is not None:
            key = obj.__class__.__name__ + "." + obj.id
            self.__objects[key] = obj

    def save(self):
        """serializes __objects to the JSON file (path: __file_path)"""
        json_objects = {}
        for key in self.__objects:
            if key == "password":
                json_objects[key].decode()
            json_objects[key] = self.__objects[key].to_dict(save_fs=1)
        with open(self.__file_path, 'w') as f:
            json.dump(json_objects, f)

    def reload(self):
        """deserializes the JSON file to __objects"""
        try:
            with open(self.__file_path, 'r') as f:
                jo = json.load(f)
            for key in jo:
                self.__objects[key] = classes[jo[key]["__class__"]](**jo[key])
        except:
            pass

    def delete(self, obj=None):
        """delete obj from __objects if it’s inside"""
        if obj is not None:
            key = obj.__class__.__name__ + '.' + obj.id
            if key in self.__objects:
                del self.__objects[key]

    def close(self):
        """call reload() method for deserializing the JSON file to objects"""
        self.reload()

    def get(self, cls, **kwargs):
        """
        Returns the object based on the class name and its ID, or
        None if not found
        """
        if cls not in classes.values():
            return None

        all_cls = models.storage.all(cls)
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

    def match_score(search_string, product_name):
        # Normalize the strings to lower case
        search_string = search_string.lower()
        product_name = product_name.lower()
        # Split the strings into words
        search_words = set(search_string.split())
        product_words = set(product_name.split())
        # Count the common words
        common_words = search_words.intersection(product_words)
        common_count = len(common_words)
        # Calculate the score based on common words and the lengths of the strings
        score = (common_count / max(len(search_words), 1)) * 100  # Score out of 100
        # Bonus: check for substring match
        if search_string in product_name:
            score += 10  # Add bonus points for exact substring match
        return score

    def search(self, cls, **kwargs):
        """
        Search for an object in the database by kwargs.
        """
        if cls not in classes.values():
            return None

        all_cls = models.storage.all(cls)
        filtered_results = []
        for value in all_cls.values():
            score = 0
            for key, v in kwargs.items():
                try:
                    x = getattr(value, key, None)
                    if x is None:
                        score=0
                    else:
                        score = FileStorage.match_score(v, x)
                except Exception as e:
                    score=0
                if score > 0:
                    break
            if score >= FileStorage.SCORETHRESHOLD:
                filtered_results.append(value)
        if (len(filtered_results) < 1):
            return None
        return filtered_results 