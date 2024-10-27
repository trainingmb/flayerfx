#!/usr/bin/python3
"""
   Holds the scraper view for:
   Carrefour
   Naivas
   QuickMart
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from difflib import SequenceMatcher

from flask import abort, jsonify, request

from models import storage
from models.price import Price
from models.product import Product
from models.store import Store

from api.v1.views import api_views
from logger import logHandler
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


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
    Inserts the scraped data into the database.

    This function processes the scraped data contained in the `crt` dictionary and updates the database accordingly. 
    It handles both new and existing products and their prices, ensuring that the latest prices are stored.

    Args:
        crt (dict): A dictionary containing the scraped data. Expected keys are:
            - 'store' (str): The name of the store.
            - 'prices' (list): A list of dictionaries, each representing a product's price information. Each dictionary should contain:
                - 'item_name' (str): The name of the product.
                - 'item_price' (float): The price of the product.
                - 'item_discount' (bool, optional): Indicates if the product is discounted.
                - 'fetched_at' (datetime, optional): The timestamp when the price was fetched.
                - 'item_link' (str, optional): The link to the product.
                - 'item_reference' (str, optional): The reference identifier for the product.

    Logs:
        - Debug logs for the start and end of the scraping process.
        - Debug logs for the number of items being processed.
        - Error logs for any exceptions encountered during the processing of products and prices.

    Raises:
        Exception: If there is an error during the bulk addition of products or prices to the database.
    """
    store_name = crt.get('store')
    logHandler.debug(f"Started {store_name} Scraper")
    
    # Fetch or create store object
    logHandler.debug(f"Fetching store object for {store_name}")
    store_obj = storage.get(Store, name=store_name)
    if store_obj is None:
        logHandler.debug(f"Store {store_name} not found, creating new store object")
        store_obj = Store(name=store_name)
        store_obj.save()
    else:
        logHandler.debug(f"Store {store_name} found")
        store_obj = store_obj[0]
    
    # Fetch existing products
    try:
        prs = crt.get('prices', [])
        logHandler.debug(f"Fetching existing products for store {store_name}")
        references = [int(i['item_reference']) for i in prs]
        logHandler.debug(f"Fetching products with references: {references}")
        all_know_products = store_obj.get_by_reference(references)
        logHandler.debug(f"Found {len(all_know_products)} out of {len(prs)} existing products for store {store_name}")
        products = {int(i.reference): i for i in all_know_products}
    except Exception as e:
        logHandler.error(f"An error occurred while fetching existing products: {repr(e)}")
        return
    # Process prices
    new_prices = []
    new_products = []
    logHandler.debug(f"Processing {len(prs)} items")
    for item in prs:
        logHandler.debug(f"Processing item: {item['item_name']} with reference: {item['item_reference']}")
        if products.get(item['item_reference'], None) is not None:
            logHandler.debug(f"Item {item['item_name']} exists in the database")
            try:
                lp = products[item['item_reference']].latest_price
                if lp is not None and lp.amount == item['item_price'] and lp.fetched_at < item.get('fetched_at', datetime.now()):
                    logHandler.debug(f"Updating latest price for item {item['item_name']}")
                    lp.update(item.get('fetched_at', datetime.now()))
                    lp.save()
                else:
                    logHandler.debug(f"Adding new price for existing item {item['item_name']}")
                    newprice = Price(product_id=products[item['item_reference']].id,
                                     amount=item['item_price'], is_discount=item['item_discount'] is not None)
                    new_prices.append(newprice)
            except Exception as e:
                logHandler.error(f"An error occurred while trying to import the product price: {item['item_name']} for an existing product\n{repr(e)}")
        else:
            logHandler.debug(f"Item {item['item_name']} does not exist in the database, creating new product")
            try:
                newproduct = Product(store_id=store_obj.id, link=item['item_link'],
                                     name=item['item_name'], reference=item['item_reference'])
                new_products.append(newproduct)
                newprice = Price(product_id=newproduct.id,
                                 amount=item['item_price'], is_discount=item['item_discount'] is not None)
                new_prices.append(newprice)
            except Exception as e:
                storage.rollback()
                logHandler.error(f"An error occurred while trying to import the product price: {item['item_name']} for a new product\n{repr(e)}")
    
    # Bulk add new products and prices
    try:
        logHandler.debug(f"Bulk adding {len(new_products)} products to {store_name}")
        storage.new(new_products)
        logHandler.debug(f"Bulk adding {len(new_prices)} prices to {store_name}")
        storage.new(new_prices)
        storage.save()
    except Exception as e:
        logHandler.error(f"An error occurred while attempting to bulk add the products:\n{repr(e)}")
    
    logHandler.debug(f"Finished {store_name} Scraper")

def ValidAPIKEY(apiKey):
    """
    Validates the provided API key against a predefined valid API key.

    Args:
        apiKey (str): The API key to be validated.

    Returns:
        bool: True if the provided API key matches the valid API key, False otherwise.
    """
    return os.getenv("FLAYERFX_VALID_API_KEY") is None or os.getenv("FLAYERFX_VALID_API_KEY")  == apiKey
    return apiKey == "9839432jnfo23i"

def ValidateScrapeJSON(crt):
    """
    Validates the JSON received from a request.

    Parameters:
    crt (dict): The JSON object to validate.

    Returns:
    int: A status code indicating the result of the validation.
        - 0: Validation successful.
        - 1: The response is not a dictionary.
        - 2: The response contains an invalid API key.
        - 6: The response is missing required keys ('store', 'api_key', 'prices').
        - 7: The response contains an invalid price record missing required keys ('item_name', 'item_link', 'item_price', 'item_reference').

    Logs warnings for various validation failures.
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
        price["item_reference"] = int(str(price["item_reference"]).strip())
    return 0

@api_views.route('/quickmart_scrape', methods=['GET', 'POST'], strict_slashes=False)
@api_views.route('/carrefour_scrape', methods=['GET', 'POST'], strict_slashes=False)
@api_views.route('/naivas_scrape', methods=['GET', 'POST'], strict_slashes=False)
@api_views.route('/generic_scrape', methods=['GET', 'POST'], strict_slashes=False)
def generic_scrape():
    """
    Retrieves the number of each objects by type.

    This function handles a request to scrape data based on a JSON payload.
    It performs the following steps:
    1. Logs the request initiation.
    2. Retrieves and validates the JSON payload from the request.
    3. If the payload is invalid or not present, it logs the error and aborts the request with a 400 status code.
    4. If the payload is valid, it submits the data to a thread pool for processing.
    5. Returns an empty JSON response.

    Returns:
        Response: An empty JSON response.

    Raises:
        400: If the request does not contain a valid JSON payload.
    """
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

def calculate_similarity_score(product1, product2):
    """
    Calculate a similarity score between two products based on their name and price.
    Args:
        product1 (Product): The first product object with 'name' and 'price' attributes.
        product2 (Product): The second product object with 'name' and 'price' attributes.
    Returns:
        float: A similarity score where a higher score indicates greater similarity.
    """
    name_similarity = SequenceMatcher(None, product1['name'], product2['name']).ratio()
    if product1['latest_price'] is None or product2['latest_price'] is None:
        return name_similarity
    price_difference = abs(product1['latest_price']['amount'] - product2['latest_price']['amount'])
    
    # Adjust the weight of name similarity and price difference as needed
    score = name_similarity - (price_difference / max(product1['latest_price']['amount'], product2['latest_price']['amount']))
    return score

def find_similar_products(product, stores, threshold=0.5):
    """
    Find similar products in specified stores based on name and price.
    
    :param product: The product to find similar products for.
    :param stores: List of stores to search in.
    :param threshold: The minimum score to consider a product as similar.
    :return: A list of similar products.
    """
    similar_products = {}
    
    def find_similar_products_in_store(store_name, s_products, product, threshold):
        similar_products = []
        logHandler.debug(f"Finding similar products for {product} in {store_name}")
        # Use a list comprehension for faster execution
        similar_products = [
            other_product for other_product in s_products
            if (score := calculate_similarity_score(product, other_product)) >= threshold
        ]
        logHandler.debug(f"Found {len(similar_products)} similar products in {store_name}")
        return store_name, similar_products

    with ThreadPoolExecutor() as executor:
        future_to_store = {executor.submit(find_similar_products_in_store, store.name, list([i.to_dict() for i in store.products]) , product, threshold): store for store in stores}
        for future in as_completed(future_to_store):
            store_name, similar_products_list = future.result()
            similar_products[store_name] = similar_products_list

    return similar_products

@api_views.route('/products/<product_id>/similar', methods=['GET'])
def get_similar_products_in_other_stores(product_id):
    """
    Get similar products in other stores based on name and price.
    
    :param product_id: The ID of the product to find similar products for.
    :return: A dictionary mapping store names to similar products.
    """
    product = storage.get(Product, id=product_id)
    if not product:
        abort(404, "{Product not found}")
    product = product[0]
    stores = list(storage.all(Store).values())
    stores.remove(product.store)
    product = product.to_dict()
    similar_products = find_similar_products(product, stores)
    
    return jsonify(similar_products)