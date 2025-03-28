from app import db

class Coordinator(db.Model):
    coordinator_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())