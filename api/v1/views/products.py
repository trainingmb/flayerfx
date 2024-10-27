#!/usr/bin/python3
""" objects that handles all default RestFul API actions for products """
from models.product import Product
from models.store import Store
from models import storage
from api.v1.views import api_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from

product_tp = {'link': str, 'name': str, 'reference': int}
page_size = 100


def dictify(v):
    if v is None:
        return None
    else:
        return v.to_dict()
    

@api_views.route('/clean/products', methods=['GET'], strict_slashes=False)
def clean_products():
    """
    Cleans all products by stripping references and returns statistics
    """
    products = storage.all(Product).values()
    changed_count = 0
    changes = []

    for product in products:
        original_reference = product.reference
        cleaned_reference = str(original_reference).strip()
        
        if original_reference != cleaned_reference:
            product.reference = cleaned_reference
            changes.append({
                'product_id': product.id,
                'original_reference': original_reference,
                'cleaned_reference': cleaned_reference
            })
            changed_count += 1
            product.save()

    storage.save()
    
    return jsonify({
        'changed_count': changed_count,
        'changes': changes
    })


@api_views.route('/products/', methods=['GET','PUT'],
                 strict_slashes=False)
#@swag_from('documentation/product/products_by_store.yml', methods=['GET'])
def all_products():
    """
    Retrieves the list of all products objects
    """
    print(request.get_json('page'))
    data = request.get_json()
    if data is not None:
        page = data.get('page',None)
        list_products = []
    for i in storage.all(Product).values():
        z = i.to_dict()
        z.update({'latest_price':dictify(i.latest_price), 'price_count':i.price_count})
        list_products.append(z)
    if page is not None and type(page) == int and page*page_size < len(list_products) and page >=1 :
        list_products = list_products[(page-1)*page_size:(page)*page_size]
    else:
        list_products = list_products[:page_size]
    return jsonify(list_products)

@api_views.route('/stores/<store_id>/products/', methods=['GET','PUT'],
                 strict_slashes=False)
#@swag_from('documentation/product/products_by_store.yml', methods=['GET'])
def get_products(store_id):
    """
    Retrieves the list of all products objects
    of a specific Store, or a specific product
    """
    list_products = []
    store = storage.get(Store, id = store_id)
    if not store:
        abort(404, "Store Not Found")
    store = store[0]
    data = request.get_json()
    if data is not None:
        page = data.get('page',None)
    list_products = []
    for i in store.products:
        z = i.to_dict()
        z.update({'latest_price':dictify(i.latest_price), 'price_count':i.price_count})
        list_products.append(z)
    if page is not None and type(page) == int and page*page_size < len(list_products) and page >=1 :
        list_products = list_products[(page-1)*page_size:(page)*page_size]
    else:
        list_products = list_products[:page_size]
    return jsonify(list_products)

@api_views.route('/stores_name/<store_name>/products/', methods=['GET','PUT'],
                 strict_slashes=False)
#@swag_from('documentation/product/products_by_store_name.yml', methods=['GET'])
def get_products_by_name(store_name):
    """
    Retrieves the list of all products objects
    of a specific Store, or a specific product
    """
    list_products = []
    store = storage.get(Store, name = store_name)
    if not store:
        abort(404, "Store Not Found")
    store = store[0]
    data = request.get_json()
    if data is not None:
        page = data.get('page',None)
    list_products = []
    for i in store.products:
        z = i.to_dict()
        z.update({'latest_price':dictify(i.latest_price), 'price_count':i.price_count})
        list_products.append(z)
    if page is not None and type(page) == int and page*page_size < len(list_products) and page >=1 :
        list_products = list_products[(page-1)*page_size:(page)*page_size]
    else:
        list_products = list_products[:page_size]
    return jsonify(list_products)

@api_views.route('/products/<product_id>/', methods=['GET'], strict_slashes=False)
#@swag_from('documentation/product/get_product.yml', methods=['GET'])
def get_product(product_id):
    """
    Retrieves a specific product based on id
    """
    product = storage.get(Product, id = product_id)
    if not product:
        abort(404, "Product Not Found")
    return jsonify(product[0].to_dict())


@api_views.route('/products/<product_id>/', methods=['DELETE'], strict_slashes=False)
#@swag_from('documentation/product/delete_product.yml', methods=['DELETE'])
def delete_product(product_id):
    """
    Deletes a product based on id provided
    """
    product = storage.get(Product, id = product_id)

    if not product:
        abort(404, "Product Not Found")
    storage.delete(product[0])
    storage.save()

    return make_response(jsonify({}), 200)


@api_views.route('/stores/<store_id>/products/', methods=['POST'],
                 strict_slashes=False)
#@swag_from('documentation/product/post_product.yml', methods=['POST'])
def post_product(store_id):
    """
    Creates a Product
    """
    store = storage.get(Store, id = store_id)
    if not store:
        abort(404, "Store Not Found")
    crt = request.get_data_json()
    if not crt:
        abort(400, description="Not a JSON")
    for i, j in product_tp.items():
        if i not in crt:
            abort(400, description="Missing " + i)
        elif type(crt[i]) != j:
            abort(400, description="Type of {} is invalid required is {} ".format(i, j))

    data = request.get_data_json()
    instance = Product(**data)
    instance.store_id = store[0].id
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)

@api_views.route('/stores_name/<store_name>/products/', methods=['POST'],
                 strict_slashes=False)
#@swag_from('documentation/product/products_by_store_name_POST.yml', methods=['POST'])
def post_products_by_name(store_name):
    """
    Creates a Product
    """
    list_products = []
    store = storage.get(Store, name = store_name)
    if not store:
        abort(404, "Store Not Found")
    store = store[0]
    crt = request.get_data_json()
    if not crt:
        abort(400, description="Not a JSON")
    for i, j in product_tp.items():
        if i not in crt:
            abort(400, description="Missing " + i)
        elif type(crt[i]) != j:
            abort(400, description="Type of {} is invalid required is {} ".format(i, j))

    data = request.get_data_json()
    instance = Product(**data)
    instance.store_id = store.id
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)

@api_views.route('/products/<product_id>/', methods=['PUT'], strict_slashes=False)
#@swag_from('documentation/product/put_product.yml', methods=['PUT'])
def put_product(product_id):
    """
    Updates a Product
    """
    product = storage.get(Product, id = product_id)
    if not product:
        abort(404, "Product Not Found")
    product = product[0]
    data = request.get_data_json()
    if not data:
        abort(400, description="Not a JSON")

    ignore = ['id', 'store_id', 'created_at', 'updated_at']

    data = request.get_data_json()
    for key, value in data.items():
        if key not in ignore:
            if key in product_tp.keys() and type(value) == product_tp[key]:
                setattr(product, key, value)
    storage.save()
    return make_response(jsonify(product.to_dict()), 200)