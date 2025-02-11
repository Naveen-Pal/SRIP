from app import db

class Coordinator(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    acronym = db.Column(db.String(10), nullable=False)
    discipline = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    unique_acr = db.Column(db.String(5), nullable=False)