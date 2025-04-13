from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_jwt_extended import JWTManager
import os 

db = SQLAlchemy()
jwt = JWTManager()
<<<<<<< HEAD
# mail = Mail()
=======
mail = Mail()

from .routes import auth_routes, coordinator_routes, faculty_routes, home_routes, prospective_intern_routes, selected_intern_routes
>>>>>>> dbc47f20582d9a7ed8a66662f89a68f595b06d3e

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
<<<<<<< HEAD
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
=======
    
>>>>>>> dbc47f20582d9a7ed8a66662f89a68f595b06d3e
    db.init_app(app)
    jwt.init_app(app)
    # mail.init_app(app)

    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(coordinator_routes.bp)
    app.register_blueprint(faculty_routes.bp)
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(prospective_intern_routes.bp)
    app.register_blueprint(selected_intern_routes.bp)

    return app