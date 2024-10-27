#!/usr/bin/python3
"""
Module: db_storage
This module defines the DBStorage class which interacts with the database.
Classes:
    DBStorage: A class that provides an interface to interact with the database.
Public Functions:
    __init__(self, engine=None): Instantiate a DBStorage object.
    all_select(self, cls, tables=[]): Query on the current database session with specific tables.
    all(self, cls=None): Query on the current database session.
    new(self, obj): Add the object to the current database session.
    save(self): Commit all changes of the current database session.
    delete(self, obj=None): Delete from the current database session obj if not None.
    reload(self): Reloads data from the database.
    close(self): Call remove() method on the private session attribute.
    rollback(self): Rollback the current session.
    get(self, cls, **kwargs): Returns the object based on the class name and its ID, or None if not found.
    count(self, cls=None): Count the number of objects in storage.
    search(self, cls, **kwargs): Search for an object in the database by kwargs.
Usage:
    This module is used to interact with the database by providing an interface to query, add, delete, and manage objects.
"""

from os import getenv
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import aliased, scoped_session, sessionmaker

from models.base_model import Base
from models.engine.matchscore import match_score, SCORETHRESHOLD

from logger import logHandler



class DBStorage:
    """
    DBStorage class for interacting with the database.
    Attributes:
        __engine (Engine): SQLAlchemy Engine instance.
        __session (Session): SQLAlchemy Session instance.
    Methods:
        __init__(self, engine=None):
            Instantiate a DBStorage object.
        all_select(self, cls, tables=[]):
            Query on the current database session with specific tables.
        all(self, cls=None):
            Query on the current database session.
        new(self, obj):
            Add the object to the current database session.
        save(self):
            Commit all changes of the current database session.
        delete(self, obj=None):
            Delete from the current database session obj if not None.
        reload(self):
            Reload data from the database.
        close(self):
            Call remove() method on the private session attribute.
        rollback(self):
            Rollback the current session.
        get(self, cls, **kwargs):
            Returns the object based on the class name and its ID, or None if not found.
        count(self, cls=None):
            Count the number of objects in storage.
        search(self, cls, **kwargs):
            Search for an object in the database by kwargs.
        get_deals(self, dateleft, dateright):
            Get deals between two dates.
    """
    __engine = None
    __session = None

    def __init__(self, engine=None):
        """
        Instantiate a DBStorage object.

        Args:
            engine (optional): SQLAlchemy engine instance. Defaults to None.

        Environment Variables:
            FLAYERFX_ENV: If set to "test", all metadata will be dropped from the engine.
        """
        self.__engine = engine
        FLAYERFX_ENV = getenv('FLAYERFX_ENV')
        if FLAYERFX_ENV == "test":
            Base.metadata.drop_all(self.__engine)

    def all_select(self, cls, tables=[]):
        """
        Query on the current database session to retrieve objects of a specified class.

        Args:
            cls (type): The class type to query.
            tables (list, optional): A list of table names to include in the query. Defaults to an empty list.

        Returns:
            dict: A dictionary where the keys are in the format 'ClassName.id' and the values are the corresponding objects.
        """
        from models.class_store import class_tables, classes
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
        """
        Query on the current database session and return a dictionary of objects.

        Args:
            cls (type, optional): The class type to filter the query. If None, query all classes.

        Returns:
            dict: A dictionary where the key is a string in the format 'ClassName.id' and the value is the object instance.
        """
        from models.class_store import classes
        new_dict = {}
        for clss in classes:
            if cls is None or cls is classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss]).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        return (new_dict)

    def new(self, obj):
        """
        Add the object to the current database session.

        If the object is a list, all objects in the list will be added to the session.
        Otherwise, the single object will be added to the session.

        Args:
            obj (object or list): The object or list of objects to add to the session.
        """
        if type(obj) == list:
            self.__session.bulk_save_objects(obj)
        else:
            self.__session.add(obj)

    def save(self):
        """
        Commits all changes of the current database session.

        This method saves any modifications made to the database session
        by committing the current transaction.
        """
        self.__session.commit()

    def delete(self, obj=None):
        """
        Deletes an object from the current database session if the object is not None.

        Args:
            obj: The object to be deleted from the session. If None, no action is taken.
        """
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """
        Reloads data from the database by creating all tables defined in the metadata
        and initializing a new session.

        This method performs the following steps:
        1. Prints the current engine being used.
        2. Creates all tables defined in the Base metadata using the engine.
        3. Configures a session factory with the engine and sets `expire_on_commit` to False.
        4. Initializes a scoped session using the session factory and assigns it to `self.__session`.
        """
        logHandler.debug(f"Engine = {self.__engine}")
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

    def close(self):
        """
        Closes the current session.

        This method calls the remove() method on the private session attribute
        to properly close and clean up the session.
        """
        self.__session.remove()

    def rollback(self):
        """
        Rollback the current session.

        This method rolls back the current transaction in the session.
        """
        self.__session.rollback()

    def get(self, cls, **kwargs):
        """
        Retrieves objects based on the class type and specified filter criteria.

        Args:
            cls (type): The class type of the objects to retrieve.
            **kwargs: Arbitrary keyword arguments used as filter criteria.

        Returns:
            list: A list of objects that match the filter criteria, or None if no objects are found.
        """
        from models.class_store import classes  
        if cls not in classes.values():
            return None
        filtered_cls = self.__session.query(cls).filter_by(**kwargs).all()
        if (len(filtered_cls) < 1):
            return None
        return filtered_cls

    def count(self, cls=None):
        """
        Count the number of objects in storage.
        Args:
            cls (type, optional): The class type to count objects for. If None, count all objects.
        Returns:
            int: The number of objects in storage.
        """
        from models.class_store import classes
        all_class = classes.values()

        if not cls:
            count = 0
            for clas in all_class:
                count += self.__session.query(clas).count()
        else:
            count = self.__session.query(cls).count()

        return count
    
    def search(self, cls, **kwargs):
        """
        Search for an object in the database by keyword arguments.

        Args:
            cls (type): The class type of the object to search for.
            **kwargs: Arbitrary keyword arguments used as search filters.

        Returns:
            list: A list of objects that match the search criteria, sorted by match score.
                  Returns None if no objects match the criteria or if the match score is below the threshold.

        Raises:
            AttributeError: If the class does not have the specified attribute in kwargs.
        """
        from models.class_store import classes
        if cls not in classes.values():
            return None
        filters = [getattr(cls, key).like(f"%{value}%") for key, value in kwargs.items()]
        filtered_cls = self.__session.query(cls).filter(or_(*filters)).all()
        filtered_results = [(match_score(kwargs['name'], value.name), value) for value in filtered_cls]
        if (len(filtered_results) < 1):
            return None
        return [i[1] for i in sorted(filtered_results, key=lambda a: a[0]) if i[0] > SCORETHRESHOLD]

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
        # Select the first Price record for each product who's fetched_at date is between dateleft and dateright
        # and the discount is True and group by product_id
        deals = self.__session.\
            query(Price).\
            filter(Price.is_discount == True).\
            group_by(Price.product_id).\
            having(func.MAX(Price.fetched_at)).\
            sort(Price.fetched_at.desc()).\
            all()
        return deals

    def get_recent_discounted_prices(self, dateleft, dateright):
        """
        Select the most recent Price record for each product where fetched_at date is between dateleft and dateright,
        the discount is True, grouped by product_id, and ordered by the price amount.

        Args:
            dateleft (datetime): The start date for the fetched_at filter.
            dateright (datetime): The end date for the fetched_at filter.

        Returns:
            List[Price]: List of Price records.
        """
        from models.price import Price
        # Create an alias for the Price table
        PriceAlias = aliased(Price)

        # Subquery to get the most recent fetched_at date for each product
        subquery = (
            self.__session.query(
                PriceAlias.product_id,
                func.max(PriceAlias.fetched_at).label('max_fetched_at')
            )
            .filter(
                and_(
                    PriceAlias.fetched_at.between(dateleft, dateright),
                    PriceAlias.is_discount == True
                )
            )
            .group_by(PriceAlias.product_id)
            .subquery()
        )

        # Main query to get the most recent Price records
        recent_prices = (
            self.__session.query(Price)
            .join(
                subquery,
                and_(
                    Price.product_id == subquery.c.product_id,
                    Price.fetched_at == subquery.c.max_fetched_at
                )
            )
            .order_by(Price.amount)
            .all()
        )

        return recent_prices
    
    def get_session(self):
        """
        Get the current session.

        Returns:
            Session: The current session.
        """
        return self.__session
