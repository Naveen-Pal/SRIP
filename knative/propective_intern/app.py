from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from prospective_intern_routes import bp as prospective_intern_bp

db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(prospective_intern_bp)

if __name__ == "__main__":
    app.run()