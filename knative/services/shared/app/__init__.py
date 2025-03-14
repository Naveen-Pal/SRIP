# services/shared/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .config import Config

db = SQLAlchemy()
mail = Mail()

def create_app(service_name):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    # mail.init_app(app)
    
    # Dynamic blueprint loading
    if service_name == 'auth':
        from .routes.auth_routes import bp as auth_bp
        app.register_blueprint(auth_bp)
    elif service_name == 'coordinator':
        from .routes.coordinator_routes import bp as coordinator_bp
        app.register_blueprint(coordinator_bp)
    
    # ... similar for other services
    
    return app