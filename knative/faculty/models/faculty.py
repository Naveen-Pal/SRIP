from database import db

class Faculty(db.Model):
    faculty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False)
    allowed = db.Column(db.Integer, nullable=False, default=0)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())