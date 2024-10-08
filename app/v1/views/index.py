#!/usr/bin/python3
"""
Index for V1 App
"""
from app.v1.views import app_views, render_template
from models import storage, storage_t
from models.base_model import Base
from models.product import Product
from models.store import Store
from models.price import Price
from logger import logHandler

classes = {"Store": Store, "Product": Product,
                "Price": Price}

@app_views.route('/home')
def home():
    """
    Home for the website
    """
    logHandler.debug("Request for Home page")
    return render_template("user/home.html")


@app_views.route('/about')
def about():
    """
    Return the JSON statistics
    for all classes
    """
    logHandler.debug("Request for About Page")
    cls = {}
    for name, cl in classes.items():
        cls[name] = storage.count(cl)
    logHandler.debug(f"Site Statisctics Retrieved: {cls}")
    return render_template("user/about.html", cls=cls, storage_t=storage_t)
