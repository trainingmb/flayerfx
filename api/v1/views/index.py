#!/usr/bin/python3
""" Index """
from models.product import Product
from models.store import Store
from models.price import Price
from models import storage
from api.v1.views import api_views
from flask import jsonify

classes = {"Store": Store, "Product": Product,
                "Price": Price}

@api_views.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """ Status of API """
    return jsonify({"status": "OK"})


@api_views.route('/stats', methods=['GET'], strict_slashes=False)
def number_objects():
    """ Retrieves the number of each objects by type """
    num_objs = {}
    for name, cl in classes.items():
        num_objs[name] = storage.count(cl)
    return jsonify(num_objs)
