from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_auth_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    import auth_routes
    app.register_blueprint(auth_routes.bp)
    return app