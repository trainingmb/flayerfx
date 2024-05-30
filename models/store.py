#!/usr/bin/python3
""" holds class store"""

import models
from models.base_model import BaseModel, Base
from models.product import Product
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class Store(BaseModel, Base):
    """Representation of a store """
    if 'db' in models.storage_t:
        __tablename__ = 'stores'
        name = Column('name', String(255), index=True, unique=True, nullable=False)
        products = relationship("Product",
                              back_populates="store",
                              cascade="all, delete, delete-orphan")
    else:
        name = ""

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs)

    if 'db' not in models.storage_t:
        @property
        def products(self):
            """getter for list of products related to the Store"""
            product_list = []
            all_products = models.storage.all(Product)
            for product in all_products.values():
                if product.store_id == self.id:
                    product_list.append(product)
            return product_list
    else:
        pass
