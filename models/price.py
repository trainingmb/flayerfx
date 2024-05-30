#!/usr/bin/python3
""" holds class Price"""

from datetime import datetime
import models
from datetime import datetime
from models.base_model import BaseModel, Base
import sqlalchemy
from sqlalchemy import Boolean, Column, Float, String, ForeignKey
from sqlalchemy.orm import relationship
import dateutil.parser


class Price(BaseModel, Base):
    """Representation of a price"""
    if 'db' in models.storage_t:
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
        """initializes price"""
        super().__init__(*args, **kwargs)
    def update(self, value=None):
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
    if 'db' not in models.storage_t:
        @property
        def product(self):
            """getter for product"""
            from models.product import Product
            prdct = models.storage.get(Product, id = self.product_id)
            if not prdct:
                return None
            return prdct[0]
