#!/usr/bin/python3
"""
Init for Views in V1
"""
from flask import Blueprint, jsonify, abort, flash, redirect, request, render_template, url_for


app_views = Blueprint('app_views', __name__, url_prefix="/app/v1")

from app.v1.forms import *

from app.v1.views.index import *
from app.v1.views.stores import *
from app.v1.views.products import *
from app.v1.views.prices import *
from app.v1.views.filterproducts import *