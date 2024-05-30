#!/usr/bin/python3
"""
Index for V1 App
"""
from app.v1.views import app_views, jsonify, render_template
from models import storage
from models.base_model import BaseModel, Base
from models.product import Product
from models.store import Store
from models.price import Price

classes = {"Store": Store, "Product": Product,
                "Price": Price}

@app_views.route('/home')
def home():
    """
    Home for the website
    """
    return render_template("user/home.html")


@app_views.route('/about')
def about():
    """
    Return the JSON statistics
    for all classes
    """
    cls = {}
    for name, cl in classes.items():
        cls[name] = storage.count(cl)
    return render_template("user/about.html", cls=cls)