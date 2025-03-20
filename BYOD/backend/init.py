from flask import Flask
from backend.route import app as routes_app

def create_app():
    """Creates and configures the Flask app"""
    app = Flask(__name__)
    
    # Register routes
    app.register_blueprint(routes_app)

    return app

