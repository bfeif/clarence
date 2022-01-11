import os
from flask import Flask

def create_app():
    
    # create app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key')
    
    # register app
    from . import checkmymate
    app.register_blueprint(checkmymate.bp)
    
    # return
    return app
