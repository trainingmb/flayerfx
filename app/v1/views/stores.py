#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Store """
from models.store import Store
from models import storage
from app.v1.forms import BaseStoreForm
from app.v1.views import app_views
from flask import abort, redirect, render_template ,request, url_for
from flasgger.utils import swag_from


@app_views.route('/stores', methods=['GET'], strict_slashes=False)
#@swag_from('documentation/store/all_stores.yml')
def all_stores():
    """
    Retrieves the list of all store objects
    or a specific store
    """
    all_stores = storage.all(Store).values()
    return render_template('user/list_stores.html', stores = all_stores)

@app_views.route('/newstore', methods=['POST', 'GET'], strict_slashes=False)
def create_store():
    """
    Create a New Store
    """
    form = BaseStoreForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            newstore_obj = Store(name=form.store_name.data)
            newstore_obj.save()
            return redirect(url_for('app_views.rud_store', store_id=newstore_obj.id))
    return render_template('user/create_store.html', form=form)

@app_views.route('/stores/<store_id>', methods=['POST', 'GET', 'DELETE'])
def rud_store(store_id):
    """
    Get/Modify/Delete store with id <store_id>
    if present else returns raises error 404
    """
    store_obj = storage.get(Store, id = store_id)
    if store_obj is None:
        abort(404, "Store not Found")
    store_obj = store_obj[0]
    if '_method' in request.form.keys() and request.form['_method'] == 'DELETE':
        store_obj.delete()
        storage.save()
        return redirect(url_for('app_views.all_stores'))
    form = BaseStoreForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            store_obj.name = form.store_name.data
            store_obj.save()
    form.store_name.data = store_obj.name
    form.submit.label.text = "Save Changes"

        # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of products per page
    products = store_obj.products
    total = len(products)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_products = products[start:end]

    return render_template('user/store_view.html',\
                           store=store_obj,\
                           products=paginated_products,\
                           form=form, page=page,\
                           per_page=per_page,\
                           total=total,\
                           total_pages=total//per_page + 1)
    return render_template('user/store_view.html', store=store_obj, products=store_obj.products, form=form)