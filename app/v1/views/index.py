#!/usr/bin/python3
"""
Module: index
This module defines the routes for the V1 App, including the home and about pages.
Classes:
    None
Public Functions:
    home(): Handles the route for the home page and renders the home template.
    about(): Handles the route for the about page, retrieves statistics for all classes, and renders the about template.
Usage:
    This module is used to define the endpoints for the home and about pages of the V1 App.
    Example:
            # Function implementation
            # Function implementation
"""

from app.v1.views import app_views, render_template
from logger import logHandler
from models import storage, storage_t
from models.class_store import classes

@app_views.route('/home')
def home():
    """
    Renders the home page for the website.

    Logs a debug message indicating a request for the home page and returns the rendered template for the home page.

    Returns:
        str: The rendered HTML template for the home page.
    """
    logHandler.debug("Request for Home page")
    return render_template("user/home.html")


@app_views.route('/about')
def about():
    """
    Handles the request for the About page.

    This function logs the request for the About page, retrieves statistics
    for all classes from the storage, logs the retrieved statistics, and
    renders the 'user/about.html' template with the class statistics and
    storage type.

    Returns:
        Response: The rendered template for the About page.
    """    
    logHandler.debug("Request for About Page")
    cls = {}
    for name, cl in classes.items():
        cls[name] = storage.count(cl)
    logHandler.debug(f"Site Statisctics Retrieved: {cls}")
    return render_template("user/about.html", cls=cls, storage_t=storage_t)
