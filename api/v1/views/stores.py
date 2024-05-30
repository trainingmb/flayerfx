#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Store """
from models.store import Store
from models import storage
from api.v1.views import api_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from


@api_views.route('/stores', methods=['GET'], strict_slashes=False)
#@swag_from('documentation/store/all_stores.yml')
def all_stores():
    """
    Retrieves the list of all store objects
    or a specific store
    """
    all_stores = storage.all(Store).values()
    list_stores = []
    for store in all_stores:
        list_stores.append(store.to_dict())
    return jsonify(list_stores)


@api_views.route('/stores/<store_id>/', methods=['GET'], strict_slashes=False)
#@swag_from('documentation/store/get_store.yml', methods=['GET'])
def get_store(store_id):
    """
    Retrieves an store
    """
    store = storage.get(Store, id = store_id)
    if not store:
        abort(404, "Store Not Found")
    return jsonify(store[0].to_dict())


@api_views.route('/stores/<store_id>/', methods=['DELETE'],
                 strict_slashes=False)
#@swag_from('documentation/store/delete_store.yml', methods=['DELETE'])
def delete_store(store_id):
    """
    Deletes a store Object
    """
    store = storage.get(Store, id = store_id)
    if not store:
        abort(404)

    storage.delete(store[0])
    storage.save()

    return make_response(jsonify({}), 200)


@api_views.route('/stores/', methods=['POST'], strict_slashes=False)
#@swag_from('documentation/store/post_store.yml', methods=['POST'])
def post_store():
    """
    Creates a store
    """
    crt = request.get_json()
    if not crt:
        abort(400, description="Not a JSON")
    for i, j in [('reference', int), ('name', str), ('link', str)]:
        if i not in crt:
            abort(400, description="Missing " + i)
        elif type(crt[i]) != j:
            abort(400, description="Type of {} is invalid required is {} ".format(i, j))

    data = request.get_json()
    instance = Store(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@api_views.route('/stores/<store_id>/', methods=['PUT'], strict_slashes=False)
#@swag_from('documentation/store/put_store.yml', methods=['PUT'])
def put_store(store_id):
    """
    Updates a store
    """
    store = storage.get(Store, id = store_id)

    if not store:
        abort(404)
    store = store[0]
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")

    ignore = ['id', 'created_at', 'updated_at']

    for key, value in data.items():
        if key not in ignore:
            setattr(store, key, value)
    storage.save()
    return make_response(jsonify(store.to_dict()), 200)