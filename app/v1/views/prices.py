#!/usr/bin/python3
"""
Module: prices
This module defines API endpoints for managing prices related to products and stores.
Public Functions:
    all_prices(): Returns a list of all prices.
    create_price(store_id, product_id): Creates a new price for a specified product in a store.
    rud_price(store_id, product_id, price_id): Retrieves, updates, or deletes a price with a specified ID.
Usage:
    This module is used to handle HTTP requests related to prices, including listing all prices, creating new prices, 
    and retrieving, updating, or deleting specific prices.
    Example:
        # To list all prices
        GET /prices
        # To create a new price for a product in a store
        POST /stores/<store_id>/product/<product_id>/newprice
        # To retrieve, update, or delete a specific price
        GET/POST/DELETE /stores/<store_id>/product/<product_id>/prices/<price_id>
"""

from datetime import datetime

from flask import abort, redirect, request, render_template, url_for

from app.v1.views import app_views
from app.v1.forms import BasePriceForm

from logger import logHandler

from models import storage
from models.price import Price
from models.product import Product
from models.store import Store
from flask import request

@app_views.route('/prices', methods=['GET'], strict_slashes=False)
@app_views.route('/prices?<int:page>&<int:per_page>', methods=['GET'], strict_slashes=False)
#TODO: Restrict this entry point
def all_prices(page=1, per_page=50):
    """
    Fetches all prices from the storage, sorts them by product ID and fetch time in descending order, 
    and returns a paginated list of prices.
    Args:
        page (int): The current page number for pagination. Defaults to 1.
        per_page (int): The number of items per page for pagination. Defaults to 50.
    Returns:
        Response: Renders the 'user/list_prices.html' template with the paginated prices, 
                  total price count, current page, and items per page.
    """
    all_prices = list(storage.all(Price).values())
    prices = sorted(all_prices, key=lambda i: (i.product_id, i.fetched_at), reverse=True)
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_prices = prices[start:end]
    
    return render_template('user/list_prices.html', prices=paginated_prices, price_count=len(prices), page=page, per_page=per_page)

@app_views.route('/orphaned/prices', methods=['GET', 'DELETE'], strict_slashes=False)
def orphaned_prices():
    """
    Fetches all orphaned prices (prices without a corresponding product) and either displays them or deletes them.
    If the request method is DELETE, the selected orphaned prices are deleted from the storage.
    Returns:
        Response: Renders the 'user/orphaned_prices.html' template with the list of orphaned prices if the method is GET.
                    Redirects to the orphaned prices view after deletion if the method is DELETE.
    """
    all_prices = list(storage.all(Price).values())
    orphaned_prices = [price for price in all_prices if storage.get(Product, id=price.product_id) is None]

    if request.method == 'DELETE':
        selected_price_ids = request.form.getlist('price_ids')
        for price in orphaned_prices:
            if str(price.id) in selected_price_ids:
                price.delete()
        storage.save()
        return redirect(url_for('app_views.orphaned_prices'))

    return render_template('user/orphaned_prices.html', prices=orphaned_prices)


@app_views.route('/stores/<store_id>/product/<product_id>/newprice', methods=['POST', 'GET'], strict_slashes=False)
def create_price(store_id, product_id):
    """
        This function handles the creation of a new price for a given product in a specified store.
        It performs the following steps:
        1. Logs the request to create a new price.
        2. Retrieves the store object based on the provided store_id.
        3. If the store is not found, logs a warning and aborts with a 404 error.
        4. Retrieves the product object based on the provided product_id.
        5. If the product is not found or does not belong to the store, logs a warning and aborts with a 404 error.
        6. Initializes a form for price creation.
        7. If the request method is POST and the form is valid:
           - Checks if the latest price is the same as the new price and updates the fetched_at timestamp if necessary.
           - Otherwise, creates a new price object and saves it.
           - Redirects to the price detail view.
        8. If the form is not valid, logs a warning.
        9. Fills the form with default values and renders the price creation template.

        Args:
            store_id (int): The ID of the store.
            product_id (int): The ID of the product.

        Returns:
            Response: The rendered template for price creation or a redirect to the price detail view.
    """    
    logHandler.debug(f"Request made to create a new price for product <{product_id}> in store <{store_id}>")
    store_obj = storage.get(Store, id = store_id)
    if store_obj is None:
        logHandler.warning(f"Store not found {store_id}")
        abort(404, "Store not Found")
    store_obj = store_obj[0]
    logHandler.debug(f"Store name {store_obj.name}")
    product_obj = storage.get(Product, id = product_id)
    if product_obj is None or product_obj[0].store_id != store_obj.id:
        logHandler.warning(f"Product not found {product_id}")
        abort(404, "Product not Found")
    else:
        product_obj = product_obj[0]
    logHandler.debug(f"Product name {product_obj.name}")
    form = BasePriceForm()
    form.price_products.choices = [(product_obj.id, product_obj.name)]
    if request.method == 'POST':
        logHandler.debug("Request method POST")
        if form.validate_on_submit():
            logHandler.debug("Form Validated")
            lp = product_obj.latest_price
            if lp is not None and lp.amount == float(form.price_amount.data) and lp.fetched_at < form.price_fetched_at.data:
                lp.update(form.price_fetched_at.data)
                lp.save()
                return redirect(url_for('app_views.rud_price', store_id=store_id, product_id=product_obj.id, price_id=lp.id))
            else:
                newprice_obj = Price(product_id=product_id, amount=float(form.price_amount.data),
                                       is_discount=form.price_is_discount.data, fetched_at=form.price_fetched_at.data)
                newprice_obj.save()
                return redirect(url_for('app_views.rud_price', store_id=store_id, product_id=product_obj.id, price_id=newprice_obj.id))
        else:
            logHandler.warning("Request with form was NOT valid")
    logHandler.debug("Filing in the form with default values")
    form.price_products.data = product_obj.id
    form.price_amount.data = 0.0
    form.price_is_discount.data = False
    form.price_fetched_at.data = datetime.now()
    return render_template('user/create_price.html', store=store_obj, product=product_obj, form=form)

@app_views.route('/stores/<store_id>/product/<product_id>/prices/<price_id>', methods=['POST', 'GET', 'DELETE'])
def rud_price(store_id, product_id, price_id):
    """
    Get/Modify/Delete price with id <price_id>
    if present else returns raises error 404
    """
    logHandler.debug(f"Request made to edit a price for product <{product_id}> in store <{store_id}> with price <{price_id}>")
    store_obj = storage.get(Store, id = store_id)
    if store_obj is None:
        logHandler.warning(f"Store not found {store_id}")
        abort(404, "Store not Found")
    store_obj = store_obj[0]
    logHandler.debug(f"Store name {store_obj.name}")
    product_obj = storage.get(Product, id = product_id)
    if product_obj is None or product_obj[0].store_id != store_obj.id:
        logHandler.warning(f"Product not found {product_id}")
        abort(404, "Product not Found")
    else:
        product_obj = product_obj[0]
    logHandler.debug(f"Product name {product_obj.name}")
    price_obj = storage.get(Price, id = price_id)
    if price_obj is None or product_obj.id != price_obj[0].product_id:
        logHandler.warning(f"Price not found {price_id}")
        abort(404, "Price not Found")
    else:
        price_obj = price_obj[0]
    logHandler.debug(f"Price value {price_obj.amount}")
    form = BasePriceForm()
    choices = [(cr.id, cr.name) for cr in storage.get(Product, store_id = store_id)]
    form.price_products.choices = choices
    if '_method' in request.form.keys() and request.form['_method'] == 'DELETE':
        logHandler.debug("Deleting the price")
        price_obj.delete()
        storage.save()
        return redirect(url_for('app_views.rud_product', store_id=store_obj.id, product_id=product_obj.id))
    if request.method == 'POST':
        logHandler.debug("Request method POST")
        if form.validate_on_submit():
            logHandler.debug("Form Validated")
            price_obj.amount = float(form.price_amount.data)
            price_obj.fetched_at = form.price_fetched_at.data
            price_obj.is_discount = form.price_is_discount.data
            if form.price_products.data != product_obj.id and form.price_products.data in \
                [i[0] for i in choices]:
                    price_obj.product_id = form.price_products.data
            price_obj.save()
        else:
            logHandler.warning("Form not valid")
    logHandler.debug("Filing in form with default value")
    form.price_is_discount.data = price_obj.is_discount
    form.price_amount.data = price_obj.amount
    form.price_fetched_at.data = price_obj.fetched_at
    form.price_products.data = price_obj.product_id
    form.submit.label.text = "Save Changes"
    return render_template('user/price_view.html', store_obj=store_obj, product=product_obj, price=price_obj, form=form)
