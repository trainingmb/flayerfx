#!/usr/bin/python3
"""
Module: product
This module defines the Product class, which represents a product with attributes such as store_id, link, name, reference, and relationships to prices and store. It utilizes SQLAlchemy for ORM and supports both database and non-database storage types.
Classes:
    Product: Represents a product with attributes and relationships to prices and store.
Public Functions:
Usage:
    # Creating a new product instance
    product = Product(name="Sample Product", link="http://example.com", reference=12345)
    # Accessing product attributes
    print(product.name)
    print(product.link)
    # Accessing related prices
    prices = product.prices
    latest_price = product.latest_price
    price_count = product.price_count
    sorted_prices = product.prices_sorted
    # Accessing related store
    store = product.store
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel, Base
from models.price import Price
from models import storage, storage_t
from models.product_relation import ProductRelation


class Product(BaseModel, Base):
    """
    Represents a product with attributes such as store_id, link, name, reference, and relationships to prices and store.
    
    Attributes:
        __tablename__ (str): The name of the table in the database.
        store_id (Column): Foreign key referencing the store's ID.
        store (relationship): Relationship to the Store model.
        link (Column): URL link related to the product.
        name (Column): Name of the product.
        reference (Column): Reference number of the product.
        prices (relationship): Relationship to the Price model with cascading delete options.
    Methods:
        __init__(*args, **kwargs): Initializes a Product instance.
        to_dict(with_latest_price=True, save_fs=None): Converts the product instance to a dictionary.
        prices (property): Retrieves the list of prices related to the product (if 'db' not in storage_t).
        store (property): Retrieves the store related to the product (if 'db' not in storage_t).
        latest_price (property): Retrieves the latest price of the product.
        price_count (property): Retrieves the count of prices related to the product.
        prices_sorted (property): Retrieves the list of prices sorted by the fetched_at attribute in descending order.
    """
    if 'db' in storage_t:
        __tablename__ = 'products'
        store_id = Column('storeid', String(60), ForeignKey('stores.id'), nullable=False)
        store = relationship('Store', back_populates='products')
        link = Column('link', String(255))
        name = Column('name', String(255), index=True, nullable=False)
        reference = Column('reference', Integer, index=True)
        prices = relationship("Price",
                              back_populates="product",
                              cascade="all, delete, delete-orphan")
        relations = relationship("ProductRelation", foreign_keys=[ProductRelation.product_id], back_populates="product")
        reverse_relations = relationship("ProductRelation", foreign_keys=[ProductRelation.related_product_id], back_populates="related_product")
    else:
        store_id = ""
        link = ""
        name = ""
        reference = 0

    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the class.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    if 'db' not in storage_t:
        @property
        def prices(self):
            """
            Returns a list of prices related to the Product.

            This method retrieves all prices from the storage and filters them
            to include only those that are associated with the current product
            instance.

            Returns:
                list: A list of Price objects related to the Product.
            """
            price_list = []
            all_prices = storage.all(Price)
            for price in all_prices.values():
                if price.product_id == self.id:
                    price_list.append(price)
            return price_list
        @property
        def store(self):
            """
            Retrieves the store associated with the current product instance.

            Returns:
                Store or None: The store object if found, otherwise None.
            """
            from models.store import Store
            sto = storage.get(Store, id=self.store_id)
            if not sto:
                return None
            return sto[0]
    else:
        pass

    def to_dict(self, with_latest_price=True, save_fs=None):
        """
        Convert the product instance to a dictionary.
        Args:
            with_latest_price (bool): If True, include the latest price in the dictionary.
            save_fs (optional): Additional parameter to pass to the superclass's to_dict method.
        Returns:
            dict: A dictionary representation of the product instance, optionally including the latest price.
        """

        a = super().to_dict(save_fs)
        if with_latest_price:
            a['latest_price'] = self.latest_price.to_dict() if self.latest_price else None
        return a

    @property
    def latest_price(self):
        """
        Returns the latest price from the sorted prices list.

        This property retrieves the first element from the `prices_sorted` list,
        which is assumed to be sorted in descending order. If the list is empty,
        it returns None.

        Returns:
            float or None: The latest price if available, otherwise None.
        """
        p = self.prices_sorted
        if len(p) < 1:
            return None
        else:
            return p[0]
    @property
    def price_count(self):
        """
        Returns the number of prices associated with the product.

        Returns:
            int: The count of prices.
        """
        return len(self.prices)    
    @property
    def prices_sorted(self):
        """
        Returns the list of prices sorted by the fetched_at attribute in descending order.
        
        Returns:
            list: A list of Price objects sorted by the fetched_at attribute in descending order.
        """
        return sorted(self.prices, key=lambda i:i.fetched_at, reverse=True)

    def rolling_avg(self, count=10):
        """
        Returns the rolling average of the prices.

        This property calculates the average of all prices associated with the product.

        Returns:
            float: The average price of the product.
        """
        if self.price_count == 0:
            return 0
        if self.price_count < count:
            count = self.price_count
        return sum([p.amount for p in self.prices_sorted[:count]]) / count

    def get_related_products(self, min_similarity=0.0):
        """
        Retrieves related products across different stores.
        
        Args:
            min_similarity (float): Minimum similarity score to consider (0.0 to 1.0)
        
        Returns:
            list: A list of tuples containing (related_product, similarity_score)
        """
        related_products = []
        for relation in self.relations:
            if relation.similarity_score >= min_similarity:
                related_products.append((relation.related_product, relation.similarity_score))
        for reverse_relation in self.reverse_relations:
            if reverse_relation.similarity_score >= min_similarity:
                related_products.append((reverse_relation.product, reverse_relation.similarity_score))
        return sorted(related_products, key=lambda x: x[1], reverse=True)

    @staticmethod
    def compare_products(product1, product2):
        """
        Compares two products and returns a similarity score.
        
        This method should be implemented to consider various factors such as:
        - Product name similarity
        - Price history similarity
        - Other relevant attributes
        
        Returns:
            float: A similarity score between 0.0 and 1.0
        """
        # Implement your comparison logic here
        # This is a placeholder implementation
        return 0.5

    @classmethod
    def update_product_relations(cls, product, potential_matches, threshold=0.7):
        """
        Updates product relations based on similarity comparisons.
        
        Args:
            product (Product): The product to update relations for
            potential_matches (list): List of potential matching products
            threshold (float): Minimum similarity score to create a relation
        """
        for potential_match in potential_matches:
            if product.id != potential_match.id and product.store_id != potential_match.store_id:
                similarity = cls.compare_products(product, potential_match)
                if similarity >= threshold:
                    relation = ProductRelation(
                        product_id=product.id,
                        related_product_id=potential_match.id,
                        similarity_score=similarity
                    )
                    storage.new(relation)
        storage.save()
