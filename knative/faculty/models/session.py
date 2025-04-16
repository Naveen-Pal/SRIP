from database import db

class Session(db.Model):
    session_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())