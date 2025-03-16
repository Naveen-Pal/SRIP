from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from auth_routes import bp as auth_bp

db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run()