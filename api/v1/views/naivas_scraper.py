#!/usr/bin/python3
""" Scraper Naivas Response Handler """
from models.price import Price
from models.store import Store
from models.product import Product
from models import storage
from api.v1.views import api_views
from flask import abort, jsonify, request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from logger import logHandler


# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
executor = ThreadPoolExecutor(2)


def threaded_nvs_scrap(crt):
    """
    Inserts the scarpped data into the database
    """
    store_name = crt.get('store')
    logHandler.debug(f"Started {store_name} Scraper")
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
        if products.get(item['item_name'], None) is not None:
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
            except Exception as e:
                logHandler.error(f"An error occured while trying to import the product price:{item['item_name']} for an existing product\n{repr(e)}")
        else:
            try:
                newproduct = Product(store_id=store_obj.id, link=item['item_link'],
                                     name=item['item_name'], reference=item['item_reference'])
                new_products.append(newproduct)
                newprice = Price(product_id = newproduct.id,
                                 amount = item['item_price'], is_discount = item['item_discount'] is not None)
                new_prices.append(newprice)
            except Exception as e:
                logHandler.error(f"An error occured while trying to import the product price:{item['item_name']} for a new product\n{repr(e)}")
    try:
        logHandler.debug("Bulk adding products naivas")
        storage.new(new_products)
        logHandler.debug("Bulk adding prices naivas")
        storage.new(new_prices)
        storage.save()
    except Exception as e:
        logHandler.error(f"An error occured while attempting to bulk add the products:\n{repr(e)}")
    logHandler.debug(f"Started {store_name} Scraper")

@api_views.route('/naivas_scrape', methods=['GET', 'POST'], strict_slashes=False)
def nvs_scrape():
    """ Retrieves the number of each objects by type """
    logHandler.debug("Request made to Naivas Scarper")
    crt = request.get_json()
    if not crt:
        logHandler.debug("Request recieved did not have a JSON value.")
        abort(400, description="Not a JSON")
    logHandler.debug("JSON sent to thread pool")
    executor.submit(threaded_nvs_scrap, crt)
    return jsonify({})