#!/usr/bin/python3
"""
Module: filterproducts
This module defines the views for filtering and searching products in a Flask web application.
Public Functions:
    sort_products(product): Sorts products based on their latest price fetch date and name.
    search_product(): Handles the search functionality for products based on user input.
    todays_discount_product(): Retrieves the list of all products on discount today.
Usage:
    This module is used to provide endpoints for searching and filtering products in the application.
    Example:
        To search for products, send a GET or POST request to the '/searchproducts' endpoint.
        To retrieve today's discount products, send a GET request to the '/discount_products' endpoint.
"""
from datetime import datetime

from flask import render_template, request

from app.v1.forms import BaseSearchProductForm
from app.v1.views import app_views
from logger import logHandler
from models import storage
from models.product import Product
from models.store import Store
from datetime import timedelta

def sort_products(product):
    """
    Sorts products based on their latest price's fetched date and name.

    If the product has a latest price, it returns a tuple containing the 
    fetched date of the latest price and the product's name. If the product 
    does not have a latest price, it returns a tuple with a default date 
    (January 1, 1970) and the product's name, ensuring such products are 
    sorted at the end.

    Args:
        product (object): The product object to be sorted. It is expected 
                          to have 'latest_price' and 'name' attributes.

    Returns:
        tuple: A tuple containing the fetched date of the latest price 
               (or a default date if no latest price) and the product's name.
    """
    if product.latest_price is not None:
        return product.latest_price.fetched_at, product.name
    else:
        # if not latest price, should be at the end
        return datetime(1970, 1, 1), product.name

@app_views.route('/searchproducts', methods=['GET', 'POST'])
def search_product(): 
    """
    Handles the product search functionality.

    This function initializes a search form, populates store choices, and processes
    the search request based on the form input. It supports searching for products
    across all stores or within a specific store. The results are then categorized
    by store and rendered in the appropriate template.

    Returns:
        str: Rendered HTML template for product search results or the search form.

    Templates:
        - 'user/product_search.html': Rendered with search results or the search form.

    Form:
        BaseSearchProductForm: The form used for searching products.

    Methods:
        GET: Renders the search form.
        POST: Processes the search request and renders the search results.

    Context Variables:
        search_string (str): The search string entered by the user.
        today (datetime): The current date and time.
        form (BaseSearchProductForm): The search form instance.
        products (list): List of products matching the search criteria.
        splitProducts (dict): Dictionary of lists of products categorized by store.

    Logs:
        - Logs the number of products found or if no products are found.
    """
    form = BaseSearchProductForm()
    choices = [(cr.id, cr.name) for cr in storage.all(Store).values()]
    choices.insert(0, (0, "All Stores"))
    form.product_stores.choices = choices
    if request.method == 'POST':
        if form.validate_on_submit():
            products = []
            if form.product_stores.data == 0:
                products = storage.search(Product, name=form.search_string.data)
            else:
                products = storage.search(Product, store_id=form.product_stores.data, name=form.search_string.data)
            if products is not None:
                logHandler.info("No of Products found: {}".format(len(products)))
                #Use the names of the stores in choices to make a dictionary of lists
                tempsplitProducts = {i[0]: [] for i in choices[1:]}
                splitProducts = {}
                for product in products:
                    tempsplitProducts[product.store_id].append(product)
                for key in tempsplitProducts.keys():
                    if len(tempsplitProducts[key]) != 0:
                        splitProducts[key] = sorted(tempsplitProducts[key], key=sort_products, reverse=True)
                del tempsplitProducts
                form.submit.label.text = "Search Again"
                return render_template('user/product_search.html', search_string=form.search_string.data, today=datetime.today(), form=form, products=products, splitProducts=splitProducts)
    form.submit.label.text = "Search For Products"
    return render_template('user/product_search.html', search_string="", today=datetime.today(), form=form, splitProducts={})

@app_views.route('/discount_products', methods=['GET'])
def todays_discount_product():
    """
    Retrieves the list of all products on discount today.

    This function fetches all products from the storage and renders them
    on the 'user/list_products.html' template.

    Returns:
        A rendered HTML template displaying the list of products on discount.
    """
    splitProducts = { store.id:{ "store": store, "products": [] } for store in storage.all(Store).values() }
    yesterday = datetime.today().date() - timedelta(days=1)
    tommorow = datetime.today().date() + timedelta(days=1)
    prices = storage.get_recent_discounted_prices(yesterday, tommorow)
    logHandler.info("No of Prices found: {}".format(len(prices)))
    for price in prices:
        product = price.product
        setattr(product, 'deal_price', price)
        setattr(product, 'roll_avg', product.rolling_avg())
        splitProducts[product.store_id]["products"].append(product)
    return render_template('user/list_products_deals.html', splitProducts = splitProducts, daterange = "Today", today=datetime.today())