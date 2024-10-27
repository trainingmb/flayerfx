#!/usr/bin/python3
"""
Module: product_relation
This module defines the ProductRelation class, which represents a relationship
between products across different stores.
"""

from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base
from models import storage_t

class ProductRelation(BaseModel, Base):
    """
    ProductRelation Model
    This class represents a relationship between products across different stores.
    """
    if 'db' in storage_t:
        __tablename__ = 'product_relations'
        product_id = Column(String(60), ForeignKey('products.id'), nullable=False)
        related_product_id = Column(String(60), ForeignKey('products.id'), nullable=False)
        similarity_score = Column(Float, default=0.0)
        
        product = relationship("Product", foreign_keys=[product_id], back_populates="relations")
        related_product = relationship("Product", foreign_keys=[related_product_id], back_populates="reverse_relations")
    else:
        product_id = ""
        related_product_id = ""
        similarity_score = 0.0

    def __init__(self, *args, **kwargs):
        """Initializes a new ProductRelation instance."""
        super().__init__(*args, **kwargs)
