#!/usr/bin/python3
""" Scraper Carrefour Response Handler """
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

def threaded_crf_scrap(crt):
    """Inserts the scarpped data into the database"""
    list_products = []
    logHandler.info("Started Carrefour")
    store_name = crt.get('store')
    store_obj = storage.get(Store, name = store_name)
    if store_obj == None:
        store_obj = Store(name = store_name)
        store_obj.save()
    else:
        store_obj = store_obj[0]
    logHandler.info(store_obj.name)
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
                                     amount = item['item_price'], is_discount = item['item_discount'] == '0% OFF')
                    new_prices.append(newprice)
                    #newprice.save()
            except Exception as e:
                logHandler.info(repr(e))
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
                logHandler.info(repr(e))
    try:
        logHandler.info("Bulk adding products carrefour")
        storage.new(new_products)
        logHandler.info("Bulk adding prices carrefour")
        storage.new(new_prices)
        storage.save()
        logHandler.info("Finished Carrefour")
    except Exception as e:
        logHandler.info(repr(e))


@api_views.route('/carrefour_scrape', methods=['GET', 'POST'], strict_slashes=False)
def crf_scrape():
    """ Retrieves the number of each objects by type """
    crt = request.get_json()
    logHandler.info(crt)
    if not crt:
        abort(400, description="Not a JSON")
    executor.submit(threaded_crf_scrap, crt)
    #ret = {'store':store_obj.to_dict(), 'new products': pds, 'new_prices':newprs}
    #logHandler.info('New Items are:\n', ret)
    return jsonify({})#ret)
