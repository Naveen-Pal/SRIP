from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .config import Config
from flask_jwt_extended import JWTManager
import os 

db = SQLAlchemy()
jwt = JWTManager()
# mail = Mail()

from .routes import faculty_routes, prospective_intern_routes,selected_intern_routes, auth_routes, home_routes, coordinator_routes
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    db.init_app(app)
    jwt.init_app(app)
    # mail.init_app(app)

    app.register_blueprint(faculty_routes.bp)
    app.register_blueprint(prospective_intern_routes.bp)
    app.register_blueprint(selected_intern_routes.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(coordinator_routes.bp)

    return app