from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_login = db.Column(db.String(60), nullable=False, unique=True)
    user_pass = db.Column(db.String(255), nullable=False)
    user_nicename = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), nullable=False, unique=True)
    user_registered = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    user_status = db.Column(db.Integer, nullable=False, default=0)
    display_name = db.Column(db.String(250), nullable=False)