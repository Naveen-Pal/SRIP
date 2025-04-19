from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from .database import db
from .config import Config

jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    # mail.init_app(app)

    # Import blueprints inside the factory function to avoid circular imports
    from .routes import auth_routes, coordinator_routes, faculty_routes, home_routes, prospective_intern_routes, selected_intern_routes
    
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(coordinator_routes.bp)
    app.register_blueprint(faculty_routes.bp)
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(prospective_intern_routes.bp)
    app.register_blueprint(selected_intern_routes.bp)

    return app