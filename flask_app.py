#!/usr/bin/python3
from os import environ, getcwd
import sys    
from models import storage
from __init__ import create_app
from flask import Flask, render_template, request, make_response, jsonify
from flask_cors import CORS
from flasgger import Swagger
from flasgger.utils import swag_from

print("Current Working directory is ", getcwd())

app = create_app('development', 'v1')
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
    request.accept_mimetypes['text/html']

@app.teardown_appcontext
def close_db(error):
    """ Close Storage """
    storage.close()

# noinspection PyUnresolvedReferences
@app.errorhandler(403)
def forbidden(error):
    if wants_json_response():
        return make_response(jsonify({'error': "Forbidden"}), 403)
    return render_template('errors/403.html', title='Forbidden', wrapper='Forbidden', err=error, error=True), 403

# noinspection PyUnresolvedReferences
@app.errorhandler(404)
def page_not_found(error):
    if wants_json_response():
        return make_response(jsonify({'error': "Page Not Found"}), 404)
    return render_template('errors/404.html', title='Page Not Found', wrapper='Page Not Found', err= error, error=True), 404

# noinspection PyUnresolvedReferences
@app.errorhandler(405)
def method_not_allowed(error):
    if wants_json_response():
        return make_response(jsonify({'error': "Method Not Allowed"}), 45)
    return render_template('errors/405.html', title='Method Not Allowed', wrapper='Method Not Allowed', err=error, error=True), 404

# noinspection PyUnresolvedReferences
@app.errorhandler(500)
def internal_server_error(error):
    if wants_json_response():
        return make_response(jsonify({'error': "Internal Server Error"}), 500)
    return render_template('errors/500.html', title='Internal Server Error', wrapper='Server Error',
                           error=True), 500

# noinspection PyUnresolvedReferences
@app.errorhandler(401)
def bad_or_missing_authentication(error):
    if wants_json_response():
        return make_response(jsonify({'error': "Unauthorized"}), 501)
    return render_template('errors/401.html', title='Unauthorized', wrapper="Unauthorized", err=error, error=True), 401

# noinspection PyUnresolvedReferences
@app.errorhandler(503)
def temporarily_unavailable(error):
    if wants_json_response():
        return make_response(jsonify({'error': "Temporarily Unavailable"}), 503)
    return render_template('errors/503.html', title="Temporarily Unavailable", wrapper="Temporarily Unavailable", err=error, error=True), 503

app.config['SWAGGER'] = {
    'title': 'A very Simple',
    'uiversion': 3
}

Swagger(app)


@app.route('/')
def hello_world():
    return 'Hello from Flask!'
