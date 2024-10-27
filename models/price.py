#!/usr/bin/python3
"""
Module: price

This module defines the Price model, which represents a price entry in the system.

Classes:
    Price: A class representing a price entry, inheriting from BaseModel and Base.

Public Functions:
    __init__(*args, **kwargs): Initializes a new instance of the Price class.
    update(value=None): Updates the fetched_at attribute with the given value.
    product: Retrieves the associated product (if 'db' not in storage_t).

Usage:
    This module is used to create and manage price entries in the system. It supports both
    database-backed storage and in-memory storage, depending on the configuration of `storage_t`.

    Example:
        # Creating a new price instance
        price = Price(product_id="12345", amount=19.99, is_discount=False)
        
        # Updating the fetched_at attribute
        price.update("2023-01-01T12:00:00Z")
        
        # Accessing the associated product
        product = price.product
"""

from datetime import datetime
import dateutil.parser

from sqlalchemy import Boolean, Column, DateTime, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base
from models import storage, storage_t


class Price(BaseModel, Base):
    """
    Price Model
    This module defines the Price class, which represents a price in the system. The class inherits from BaseModel and Base.
    Attributes:
        __tablename__ (str): The name of the table in the database (if 'db' in storage_t).
        product_id (str): The ID of the associated product.
        product (relationship): The relationship to the Product model.
        fetched_at (datetime): The timestamp when the price was fetched.
        amount (float): The amount of the price.
        is_discount (bool): Indicates if the price is a discount.
    Methods:
        __init__(*args, **kwargs): Initializes a new instance of the Price class.
        update(value=None): Updates the fetched_at attribute with the given value.
        product: Retrieves the associated product (if 'db' not in storage_t).
    """
    if 'db' in storage_t:
        __tablename__ = 'prices'
        product_id = Column('productid', String(60), ForeignKey('products.id'), nullable=False)
        product = relationship('Product', back_populates='prices')
        fetched_at = Column(DateTime, default=datetime.utcnow)
        amount = Column('amount', Float)
        is_discount = Column('is_discount', Boolean(1))
    else:
        product_id = ""
        fetched_at = datetime.now()
        amount = 0.0
        is_discount = False

    def __init__(self, *args, **kwargs):
        """
        Initializes the price object with given arguments.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
    def update(self, value=None):
        """
        Updates the 'fetched_at' attribute of the instance.
        Args:
        value (str, datetime, or None): The value to set for 'fetched_at'.
            - If a string is provided, it attempts to parse it as a date.
            - If a datetime object is provided, it sets 'fetched_at' to this value.
            - If None or any other type is provided, it sets 'fetched_at' to the current datetime.
        Raises:
        ValueError: If the string cannot be parsed as a date.
        dateutil.parser._parser.ParserError: If the string cannot be parsed as a date.
        """
        if type(value) is str:
            try:
                setattr(self, 'fetched_at', dateutil.parser.parse(value))
            except ValueError:
                setattr(self, 'fetched_at', value)
            except dateutil.parser._parser.ParserError:
                setattr(self, 'fetched_at', value)
        elif type(value) is datetime:
            setattr(self, 'fetched_at', value)
        else:
            setattr(self, 'fetched_at', datetime.now())
    if 'db' not in storage_t:
        @property
        def product(self):
            """
            Retrieves the product associated with the current instance.

            This method fetches the product from the storage using the product ID 
            of the current instance. If the product is not found, it returns None.

            Returns:
                Product or None: The product instance if found, otherwise None.
            """
            from models.product import Product
            prdct = storage.get(Product, id = self.product_id)
            if not prdct:
                return None
            return prdct[0]
