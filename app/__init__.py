from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .config import Config

db = SQLAlchemy()
mail = Mail()

from .routes import faculty_routes, prospective_intern_routes,selected_intern_routes, auth_routes, home_routes, coordinator_routes
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    # mail.init_app(app)

    app.register_blueprint(faculty_routes.bp)
    app.register_blueprint(prospective_intern_routes.bp)
    app.register_blueprint(selected_intern_routes.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(coordinator_routes.bp)

    return app

def create_auth_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(auth_routes.bp)
    return app

def create_coordinator_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(coordinator_routes.bp)
    return app

def create_faculty_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(faculty_routes.bp)
    return app

def create_prospective_intern_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(prospective_intern_routes.bp)
    return app

def create_selected_intern_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(selected_intern_routes.bp)
    return app