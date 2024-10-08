#!/usr/bin/python3
""" holds class Product"""

import models
from models.base_model import BaseModel, Base
from models.price import Price
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Product(BaseModel, Base):
    """Representation of a product """
    if 'db' in models.storage_t:
        __tablename__ = 'products'
        store_id = Column('storeid', String(60), ForeignKey('stores.id'), nullable=False)
        store = relationship('Store', back_populates='products')
        link = Column('link', String(255))
        name = Column('name', String(255), index=True, nullable=False)
        reference = Column('reference', Integer, index=True)
        prices = relationship("Price",
                              back_populates="product",
                              cascade="all, delete, delete-orphan")
    else:
        store_id = ""
        link = ""
        name = ""
        reference = 0

    def __init__(self, *args, **kwargs):
        """initializes product"""
        super().__init__(*args, **kwargs)

    if 'db' not in models.storage_t:
        @property
        def prices(self):
            """getter for list of prices related to the Product"""
            price_list = []
            all_prices = models.storage.all(Price)
            for price in all_prices.values():
                if price.product_id == self.id:
                    price_list.append(price)
            return price_list
        @property
        def store(self):
            """getter for store"""
            from models.store import Store
            sto = models.storage.get(Store, id=self.store_id)
            if not sto:
                return None
            return sto[0]
    else:
        pass
    @property
    def latest_price(self):
        p = self.prices_sorted
        if len(p) < 1:
            return None
        else:
            return p[0]
    @property
    def price_count(self):
        return len(self.prices)    
    @property
    def prices_sorted(self):
        return sorted(self.prices, key=lambda i:i.fetched_at, reverse=True)
        
