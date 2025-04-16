#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Main application entry point for Bana
# Author: dreampuf (original), updated by Codegen

import os
import sys
import logging
from flask import Flask, request, redirect, url_for, render_template, abort, jsonify
from google.cloud import ndb

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='static/views')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Datastore client
client = ndb.Client()

# Middleware to provide datastore context
def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)
    return middleware

app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)

# Import routes after app initialization to avoid circular imports
from routes.blog import blog_routes
from routes.admin import admin_routes

# Register blueprints
app.register_blueprint(blog_routes)
app.register_blueprint(admin_routes, url_prefix='/admin')

@app.route('/_ah/warmup')
def warmup():
    """App Engine warmup handler"""
    return '', 200

if __name__ == '__main__':
    # This is used when running locally
    app.run(host='127.0.0.1', port=8080, debug=True)
