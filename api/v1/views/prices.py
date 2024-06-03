#!/usr/bin/python3
""" objects that handles all default RestFul API actions for prices """
from models.price import Price
from models.store import Store
from models.product import Product
from models import storage
from api.v1.views import api_views
from flask import abort, jsonify, make_response, request
from datetime import datetime
import dateutil.parser
from flasgger.utils import swag_from
from regex import match
from concurrent.futures import ThreadPoolExecutor

# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
executor = ThreadPoolExecutor(2)

price_tp = {'amount': str, 'is_discount': bool}
time = "%Y-%m-%dT%H:%M:%S.%f"

@api_views.route('/stores/<store_id>/products/<product_id>/prices', methods=['GET'],
                 strict_slashes=False)
#@swag_from('documentation/price/prices_by_product.yml', methods=['GET'])
def get_prices(store_id, product_id):
    """
    Retrieves the list of all prices objects
    of a specific Product, or a specific price
    """
    list_prices = []
    store = storage.get(Store, id = store_id)
    if not store:
        abort(404, "Store Not Found")
    store = store[0]
    product = storage.get(Product, id = product_id)
    if not product or store.id != product[0].store_id:
        abort(404, "Product Not Found")
    product = product[0]
    for price in product.prices:
        list_prices.append(price.to_dict())
    return jsonify(list_prices)


@api_views.route('/prices/<price_id>/', methods=['GET'], strict_slashes=False)
#@swag_from('documentation/price/get_price.yml', methods=['GET'])
def get_price(price_id):
    """
    Retrieves a specific price based on id
    """
    price = storage.get(Price, id = price_id)
    if not price:
        abort(404, "Price Not Found")
    price = price[0]
    return jsonify(price.to_dict())


@api_views.route('/prices/<price_id>', methods=['DELETE'], strict_slashes=False)
#@swag_from('documentation/price/delete_price.yml', methods=['DELETE'])
def delete_price(price_id):
    """
    Deletes a price based on id provided
    """
    price = storage.get(Price, id = price_id)
    if not price:
        abort(404, "Price Not Found")
    price = price[0]
    storage.delete(price)
    storage.save()

    return make_response(jsonify({}), 200)


@api_views.route('/stores/<store_id>/products/<product_id>/prices', methods=['POST'],
                 strict_slashes=False)
#@swag_from('documentation/price/price_price.yml', methods=['POST'])
def post_price(store_id, product_id):
    """
    Creates a Price
    """
    store = storage.get(Store, id = store_id)
    if not store:
        abort(404, "Store Not Found")
    store = store[0]
    product = storage.get(Product, id = product_id)
    if not product or store.id != product[0].store_id:
        abort(404, "Product Not Found")
    product = product[0]
    crt = request.get_json()
    if not crt:
        abort(400, description="Not a JSON")
    for i, j in price_tp.items():
        if i not in crt:
            abort(400, description="Missing " + i)
        elif type(crt[i]) != j:
            abort(400, description="Type of {} is invalid required is {} ".format(i, j))

    data = request.get_json()
    lp = product.latest_price
    if lp is not None and lp.amount == data.amount \
      and lp.fetched_at < data.get('fetched_at',datetime.now()):
        lp.update(data.get('fetched_at',datetime.now()))
        lp.save()
        return make_response(jsonify(lp.to_dict()), 200)
    else:
        instance = Price(**data)
        instance.product_id = product.id
        instance.save()
        return make_response(jsonify(instance.to_dict()), 201)


@api_views.route('/prices/<price_id>', methods=['PUT'], strict_slashes=False)
#@swag_from('documentation/price/put_price.yml', methods=['PUT'])
def put_price(price_id):
    """
    Updates a Price
    """
    price = storage.get(Price, id = price_id)
    if not product:
        abort(404, "Product Not Found")
    price = price[0]
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")

    ignore = ['id', 'product_id', 'created_at', 'updated_at']

    data = request.get_json()
    for key, value in data.items():
        if key not in ignore:
            if key in price_tp.keys() and type(value) == price_tp[key]:
                setattr(price, key, value)
    storage.save()
    return make_response(jsonify(price.to_dict()), 200)


def threaded_crf_scrap(crt):
    """Inserts the scarpped data into the database"""
    list_products = []
    print("Started Carrefour")
    store_name = crt.get('store')
    store_obj = storage.get(Store, name = store_name)
    if store_obj == None:
        store_obj = Store(name = store_name)
        store_obj.save()
    else:
        store_obj = store_obj[0]
    products = {i.name:i for i in store_obj.products}
    prs = crt.get('prices', [])
    new_prices = []
    new_products = []
    for item in prs:
        if item['item_name'] in products.keys():
            try:
                lp = products[item['item_name']].latest_price
                if(lp is not None and lp.amount == item['item_price']) \
                  and lp.fetched_at < item.get('fetched_at',datetime.now()):
                    lp.update(item.get('fetched_at',datetime.now()))
                    lp.save()
                else:
                    newprice = Price(product_id = products[item['item_name']].id,
                                     amount = item['item_price'], is_discount = item['item_discount'] == '0% OFF')
                    new_prices.append(newprice)
                    #newprice.save()
            except Exception as e:
                print(repr(e))
        else:
            try:
                newproduct = Product(store_id=store_obj.id, link=item['item_link'],
                                     name=item['item_name'], reference=int(item['item_link'].split('/')[-1]))
                new_products.append(newproduct)
                #newproduct.save()
                newprice = Price(product_id = newproduct.id,
                                 amount = item['item_price'], is_discount = item['item_discount'] == '0% OFF')
                new_prices.append(newprice)
                #newprice.save()
            except Exception as e:
                print(repr(e))
    storage.add(new_products)
    storage.add(new_prices)
    storage.save()
    print("Finished Carrefour")


@api_views.route('/carrefour_scrape', methods=['GET', 'POST'], strict_slashes=False)
def crf_scrape():
    """ Retrieves the number of each objects by type """
    crt = request.get_json()
    #print(crt)
    if not crt:
        abort(400, description="Not a JSON")
    executor.submit(threaded_crf_scrap, crt)
    #ret = {'store':store_obj.to_dict(), 'new products': pds, 'new_prices':newprs}
    #print('New Items are:\n', ret)
    return jsonify({})#ret)

def threaded_nvs_scrap(crt):
    """Inserts the scarpped data into the database"""
    list_products = []
    print("Started Naivas")
    store_name = crt.get('store')
    store_obj = storage.get(Store, name = store_name)
    if store_obj == None:
        store_obj = Store(name = store_name)
        store_obj.save()
    else:
        store_obj = store_obj[0]
    products = {i.name:i for i in store_obj.products}
    prs = crt.get('prices', [])
    for item in prs:
        if item['item_name'] in products.keys():
            try:
                lp = products[item['item_name']].latest_price
                if(lp is not None and lp.amount == item['item_price']) \
                  and lp.fetched_at < item.get('fetched_at',datetime.now()):
                    lp.update(item.get('fetched_at',datetime.now()))
                    lp.save()
                else:
                    newprice = Price(product_id = products[item['item_name']].id,
                                 amount = item['item_price'], is_discount = item['item_discount'] is not None)
                    new_prices.append(newprice)
                    #newprice.save()
            except Exception as e:
                print(repr(e))
        else:
            try:
                newproduct = Product(store_id=store_obj.id, link=item['item_link'],
                                     name=item['item_name'], reference=item['item_reference'])
                new_products.append(newproduct)
                #newproduct.save()
                newprice = Price(product_id = newproduct.id,
                                 amount = item['item_price'], is_discount = item['item_discount'] is not None)
                new_prices.append(newprice)
                #newprice.save()
            except Exception as e:
                print(repr(e))
    storage.add(new_products)
    storage.add(new_prices)
    storage.save()
    print("Finished Naivas")

@api_views.route('/naivas_scrape', methods=['GET', 'POST'], strict_slashes=False)
def nvs_scrape():
    """ Retrieves the number of each objects by type """
    crt = request.get_json()
    #print(crt)
    if not crt:
        abort(400, description="Not a JSON")
    executor.submit(threaded_nvs_scrap, crt)
    #ret = {'store':store_obj.to_dict(), 'new products': pds, 'new_prices':newprs}
    #print('New Items are:\n', ret)
    return jsonify({})#ret)
