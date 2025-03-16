from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

import prospective_intern_routes
app.register_blueprint(prospective_intern_routes.bp)

if __name__ == "__main__":
    app.run()