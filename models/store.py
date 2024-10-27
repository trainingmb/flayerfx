#!/usr/bin/python3
"""
Module: store
Defines the Store class which represents a store entity in the application.
Classes:
    Store: A class representing a store, inheriting from BaseModel and Base.
Usage:
    The Store class can be used to create and manage store entities within the application.
    It supports both database and non-database storage types, with appropriate handling
    for each type.
    Example:
        # Creating a new store instance
        new_store = Store(name="My Store")
        # Accessing related products (for non-database storage)
        products = new_store.products
"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

import models
from models.base_model import BaseModel, Base
from models.product import Product


class Store(BaseModel, Base):
    """
    Store Model
    This module defines the Store class, which represents a store in the application. The Store class inherits from BaseModel and Base, and it includes attributes and relationships relevant to a store.
    Attributes:
        __tablename__ (str): The name of the table in the database, set to 'stores' if 'db' is in models.storage_t.
        name (str): The name of the store, which is a unique and non-nullable string with a maximum length of 255 characters.
        products (relationship or property): A relationship to the Product model, with cascading delete options if 'db' is in models.storage_t. Otherwise, a property that returns a list of products related to the store.
    Methods:
        __init__(*args, **kwargs): Initializes a new instance of the Store class.
        products (property): If 'db' is not in models.storage_t, this property returns a list of products related to the store by checking the store_id attribute of each product.
    """
    if 'db' in models.storage_t:
        __tablename__ = 'stores'
        name = Column('name', String(255), index=True, unique=True, nullable=False)
        products = relationship("Product",
                              back_populates="store",
                              cascade="all, delete, delete-orphan")
    else:
        name = ""

    def __init__(self, *args, **kwargs):
        """
        Initializes the store with the given arguments.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    if 'db' not in models.storage_t:
        @property
        def products(self):
            """
            Returns:
                list: A list of Product instances that are related to the Store.
            """
            product_list = []
            all_products = models.storage.all(Product)
            for product in all_products.values():
                if product.store_id == self.id:
                    product_list.append(product)
            return product_list
        def get_by_reference(self, product_references):
            """
            Returns:
                list: A list of Product instances that are related to the Store that are in the product_ids list
            """
            if type(product_references) is not list:
                product_references = [product_references]
            return [i for i in self.products if i.reference in product_references]
    else:
        def get_by_reference(self, product_references):
            """
            Returns:
                list: A list of Product instances that are related to this Store and have IDs in the product_ids list.
            """
            from sqlalchemy import and_
            from models.product import Product

            if type(product_references) is not list:
                product_references = [product_references]

            return models.storage.get_session().query(Product).\
                    filter(and_(
                        Product.store_id == self.id,
                        Product.reference.in_(product_references)
                    )).\
                    all()
