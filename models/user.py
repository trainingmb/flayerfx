#!/usr/bin/python3
""" holds class Post"""

import models
from datetime import datetime
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from hashlib import md5


class User(BaseModel, Base):
    """Representation of a user"""
    if models.storage_t == 'db':
        __tablename__ = 'posts'
        creation_id = Column('creationid', String(60), ForeignKey('creations.id'), nullable=False)
        creation = relationship('Creation', back_populates='posts')
        title = Column('title', String(255))
        content = Column('content', String(65535))
        comment = Column('comment', String(255))
        reference = Column('reference', Integer, nullable=False)
        posted_at = Column(DateTime)
        fetched_at = Column(DateTime)
    else:
        creation_id = ""
        title = ""
        content = ""
        comment = ""
        reference = 0
        posted_at = datetime.utcnow()
        fetched_at = datetime.utcnow()

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs)
    if models.storage_t != "db":
        @property
        def creation(self):
            """getter for creation"""
            from models.creation import Creation
            crtion = models.storage.get(Creation, creation_id)
            return crtion
