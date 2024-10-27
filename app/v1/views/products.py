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

@app_views.route('/products', methods=['GET'], strict_slashes=False)
#@swag_from('documentation/product/products_by_store.yml', methods=['GET'])
def all_products():
    """
    Retrieves the list of all products objects with pagination
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    products = list(storage.all(Product).values())
    total = len(products)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_products = products[start:end]
    
    return render_template('user/list_products.html', 
                           products=paginated_products, 
                           page=page, 
                           per_page=per_page, 
                           total=total,
                           total_pages=total//per_page + 1)

@app_views.route('/orphaned/products', methods=['GET', 'POST'], strict_slashes=False)
def orphaned_products():
    """
    Retrieves the list of orphaned products (products without a valid store_id)
    and allows updating or deleting them.
    """
    products = list(storage.all(Product).values())
    stores = set([store.id for store in storage.all(Store).values()])
    orphaned = [product for product in products if product.store_id not in stores]
    
    if request.method == 'POST':
        action = request.form.get('action')
        selected_products = request.form.getlist('product_ids')
        if action == 'delete':
            for product_id in selected_products:
                product = storage.get(Product, id=product_id)
                if product:
                    product.delete()
                    storage.save()
        elif action == 'assign':
            new_store_id = request.form.get('store_id')
            if new_store_id in stores:
                for product_id in selected_products:
                    product = storage.get(Product, id=product_id)
                    if product:
                        product.store_id = new_store_id
                        product.save()
                        storage.save()
        return redirect(url_for('app_views.orphaned_products'))

    all_stores = storage.all(Store).values()
    return render_template('user/orphaned_products.html', products=orphaned, stores=all_stores)

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


@app_views.route('/stores/<store_id>/merge_products', methods=['GET'])
def merge_products(store_id):
    """
    Merge products with the same reference number into one product entry
    """
    store_obj = storage.get(Store, id=store_id)
    if store_obj is None:
        abort(404, "Store not Found")
    store_obj = store_obj[0]
    
    products = store_obj.products
    products_by_reference = {}
    
    for product in products:
        if product.reference not in products_by_reference:
            products_by_reference[product.reference] = []
        products_by_reference[product.reference].append(product)
    
    from models.price import Price
    changes_count = {
        'prices_moved': 0,
        'products_deleted': 0,
        'prices_deleted': 0
    }
    count = 1
    for reference, product_list in products_by_reference.items():
        products_deleted = []
        if len(product_list) > 1:
            main_product = product_list[0]
            for product in product_list[1:]:
                for price in product.prices:
                    price.product_id = main_product.id
                    price.save()
                    changes_count['prices_moved'] += 1
                products_deleted.append(product.name)
                product.delete()
                changes_count['products_deleted'] += 1
            main_product.save()
            print(f"Merged products with reference {reference}: {changes_count}")
            print(f"Products deleted: {products_deleted}")
        print(f"Product number {count} of {len(products_by_reference)}")
        count += 1

    print(f"Total changes made: {changes_count}")
    
    storage.save()
    return redirect(url_for('app_views.rud_store', store_id=store_id))