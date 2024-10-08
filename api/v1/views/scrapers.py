#!/usr/bin/python3
"""
   Holds the scraper view for:
   Carrefour
   Naivas
   QuickMart
"""
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
executor = ThreadPoolExecutor(3)

data_structure = """
    {
        'store'<string, required> : Name of the store,
        'api_key' <string, required> : Valid Api Key for the user,
        'prices' <list of dictionary> : Price Dictionary
            [
                {
                    'item_name' <string, required>: Unique name of the item,
                    'item_link' <string, required>: In store link to the item,
                    'item_price' <float, required>: Price of the product,
                    'item_discount' <float>: Stated discount on the item. The difference between current price and previous stated price,
                    'item_reference' <string, required>: Store product id used to add the product to the cart,
                },
                ...
            ]
    }
"""

def threaded_database_updater(crt):
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
        logHandler.debug(f"Bulk adding products {store_name}") 
        storage.new(new_products)
        logHandler.debug(f"Bulk adding prices {store_name}")
        storage.new(new_prices)
        storage.save()
    except Exception as e:
        logHandler.error(f"An error occured while attempting to bulk add the products:\n{repr(e)}")
    logHandler.debug(f"Finished {store_name} Scraper")

def ValidAPIKEY(apiKey):
    return apiKey == "9839432jnfo23i"

def ValidateScrapeJSON(crt):
    """
        Validate the json recieved from a request
    """
    if type(crt) is not dict:
        logHandler.warning("Response is not a dict")
        return 1
    for i in ['store', 'api_key', 'prices']:
        if i not in crt.keys():
            logHandler.warning(f"Response is does not contain {i}")
            return 6
    if not ValidAPIKEY(crt['api_key']):
        logHandler.warning(f"Response is does not contain a valid API Key")
        return 2
    for price in crt['prices']:
        for key in ["item_name", "item_link", "item_price", "item_reference"]:
            if key not in price.keys():
                logHandler.warning(f"Response contains an invalid price record {price} which is missing {key}")
                return 7
    return 0

@api_views.route('/quickmart_scrape', methods=['GET', 'POST'], strict_slashes=False)
@api_views.route('/carrefour_scrape', methods=['GET', 'POST'], strict_slashes=False)
@api_views.route('/naivas_scrape', methods=['GET', 'POST'], strict_slashes=False)
@api_views.route('/generic_scrape', methods=['GET', 'POST'], strict_slashes=False)
def generic_scrape():
    """ Retrieves the number of each objects by type """
    logHandler.debug("Request made to Scarper")
    crt = request.get_json()
    if not crt:
        logHandler.debug("Request recieved did not have a JSON value.")
        abort(400, description=f"Not a JSON. Expected structure:{data_structure}")
    validationResponse = ValidateScrapeJSON(crt)
    if validationResponse != 0:
        logHandler.debug("Request recieved JSON was not valid.")
        abort(400, description=f"Not a valid JSON. Expected structure:{data_structure}")    
    logHandler.debug("JSON sent to thread pool")
    executor.submit(threaded_database_updater, crt)
    return jsonify({})