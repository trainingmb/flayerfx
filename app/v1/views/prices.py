#!/usr/bin/python3
"""
API Base for Product based actions
"""
from app.v1.views import app_views, jsonify, abort, redirect, request, render_template, url_for
from app.v1.views import BasePriceForm
from models import storage
from models.store import Store
from models.product import Product
from models.price import Price
from datetime import datetime


@app_views.route('/prices', methods=['GET'], strict_slashes=False)
def all_prices():
    """
    Returns a list of all prices
    """
    all_product = {}
    for i in storage.all(Product).values():
        all_product[i.id] = i
    all_prices = storage.all(Price).values()
    prices=sorted(all_prices, key=lambda i:(i.product_id, i.fetched_at), reverse=True)
    return render_template('user/list_prices.html', prices=prices, product=all_product)

@app_views.route('/stores/<store_id>/product/<product_id>/newprice', methods=['POST', 'GET'], strict_slashes=False)
def create_price(store_id, product_id):
    """
    Create a New Price
    """
    store_obj = storage.get(Store, id = store_id)
    if store_obj is None:
        abort(404, "Store not Found")
    store_obj = store_obj[0]
    product_obj = storage.get(Product, id = product_id)
    if product_obj is None or product_obj[0].store_id != store_obj.id:
        abort(404, "Product not Found")
    else:
        product_obj = product_obj[0]
    form = BasePriceForm()
    form.price_products.choices = [(product_obj.id, product_obj.name)]
    if request.method == 'POST':
        if form.validate_on_submit():
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
    store_obj = storage.get(Store, id = store_id)
    if store_obj is None:
        abort(404, "Store not Found")
    store_obj = store_obj[0]
    product_obj = storage.get(Product, id = product_id)
    if product_obj is None or product_obj[0].store_id != store_obj.id:
        abort(404, "Product not Found")
    else:
        product_obj = product_obj[0]
    price_obj = storage.get(Price, id = price_id)
    if price_obj is None or product_obj.id != price_obj[0].product_id:
        abort(404, "Price not Found")
    else:
        price_obj = price_obj[0]
    form = BasePriceForm()
    choices = [(cr.id, cr.name) for cr in storage.get(Product, store_id = store_id)]
    form.price_products.choices = choices
    if '_method' in request.form.keys() and request.form['_method'] == 'DELETE':
        price_obj.delete()
        storage.save()
        return redirect(url_for('app_views.rud_product', store_id=store_obj.id, product_id=product_obj.id))
    if request.method == 'POST':
        if form.validate_on_submit():
            price_obj.amount = float(form.price_amount.data)
            price_obj.fetched_at = form.price_fetched_at.data
            price_obj.is_discount = form.price_is_discount.data
            if form.price_products.data != product_obj.id and form.price_products.data in \
                [i[0] for i in choices]:
                    price_obj.product_id = form.price_products.data
            price_obj.save()
    form.price_is_discount.data = price_obj.is_discount
    form.price_amount.data = price_obj.amount
    form.price_fetched_at.data = price_obj.fetched_at
    form.price_products.data = price_obj.product_id
    form.submit.label.text = "Save Changes"
    return render_template('user/price_view.html', store_obj=store_obj, product=product_obj, price=price_obj, form=form)
