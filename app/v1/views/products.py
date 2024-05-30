#!/usr/bin/python3
""" objects that handles all default RestFul API actions for products """
from models.product import Product
from models.store import Store
from models import storage
from app.v1.forms import BaseProductForm
from app.v1.views import app_views
from flask import abort,redirect, render_template, request, url_for
from flasgger.utils import swag_from
from datetime import datetime

product_tp = {'link': str, 'name': str, 'reference': int}

@app_views.route('/products', methods=['GET'],
                 strict_slashes=False)
#@swag_from('documentation/product/products_by_store.yml', methods=['GET'])
def all_products():
    """
    Retrieves the list of all products objects
    """
    products = storage.all(Product).values()
    return render_template('user/list_products.html', products = products)

@app_views.route('/stores/<store_id>/newproduct', methods=['POST', 'GET'], strict_slashes=False)
def create_product(store_id):
    """
    Create a New Product
    """
    store_obj = storage.get(Store, id = store_id)
    if store_obj is None:
        abort(404, "Store not Found")
    store_obj = store_obj[0]
    form = BaseProductForm()
    form.product_stores.choices = [(store_obj.id, store_obj.name)]
    form.product_stores.data = store_obj.id
    if request.method == 'POST':
        if form.validate_on_submit():
            newproduct_obj = Product(store_id=store_id, name=form.product_name.data, \
                                     link=form.product_link.data, reference=form.product_reference.data)
            newproduct_obj.save()
            return redirect(url_for('app_views.rud_product', store_id=store_id, product_id=newproduct_obj.id))
    return render_template('user/create_product.html', store=store_obj, form=form)

@app_views.route('/stores/<store_id>/products/<product_id>', methods=['POST', 'GET', 'DELETE'])
def rud_product(store_id, product_id):
    """
    Get/Modify/Delete product with id <product_id>
    if present else returns raises error 404
    """
    store_obj = storage.get(Store, id = store_id)
    if store_obj is None:
        abort(404, "Store not Found")
    store_obj = store_obj[0]    
    product_obj = storage.get(Product, id = product_id)
    form = BaseProductForm()
    choices = [(cr.id, cr.name) for cr in storage.all(Store).values()]
    form.product_stores.choices = choices
    if product_obj is None or product_obj[0].store_id != store_obj.id:
        abort(404, "Product not Found")
    else:
        product_obj = product_obj[0]
    if '_method' in request.form.keys() and request.form['_method'] == 'DELETE':
        product_obj.delete()
        storage.save()
        return redirect(url_for('app_views.all_products'))
    if request.method == 'POST':
        if form.validate_on_submit():
            product_obj.name = form.product_name.data
            product_obj.link = form.product_link.data
            product_obj.reference = form.product_reference.data
            if form.product_stores.data != store_obj.id and form.product_stores.data in \
                [i[0] for i in choices]:
                    product_obj.store_id = form.product_stores.data
            product_obj.save()
    form.product_name.data = product_obj.name
    form.product_reference.data = product_obj.reference
    form.product_link.data = product_obj.link
    form.product_stores.data = product_obj.store_id
    form.submit.label.text = "Save Changes"
    prices=product_obj.prices_sorted
    return render_template('user/product_view.html', product=product_obj, prices=prices, today=datetime.today(), form=form)