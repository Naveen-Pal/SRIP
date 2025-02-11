from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .config import Config

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    from .routes import admin_routes, faculty_routes, intern_routes, auth_routes, home_routes, coordinator_routes
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(faculty_routes.bp)
    app.register_blueprint(intern_routes.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(coordinator_routes.bp)

    return app