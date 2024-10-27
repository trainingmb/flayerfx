#!/usr/bin/python3
"""
Contains the class Store
"""
from models.store import Store
from models.product import Product
from models.price import Price


classes = {"Store": Store, "Product": Product,
          "Price": Price}
class_tables = {"Store": [ Store.name ],
          "Product": [ Product.store_id, Product.name, Product.link ],
          "Price": [ Price.product_id, Price.amount, Price.is_discount ]}
fields = {"Store": [['name', 'str', 'Name of the Store']],
          "Product": [['store_id', 'str', 'ID of the Store'],
                       ['link', 'str', 'Link to the Product in the Store'],
                       ['name', 'str', 'Name of the Product'],
                       ['reference', 'int', 'Reference Number']],
          "Price": [['product_id','str','ID of the Product'],
                   ['amount', 'float', 'Price Amount'],
                   ['is_discount', 'bool', 'The is price discounted']]}