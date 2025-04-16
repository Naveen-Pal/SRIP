from app.database import db
from datetime import datetime

class WeeklySubmission(db.Model):
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    intern_id = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, nullable=False)
    faculty_id = db.Column(db.Integer, nullable=False)
    submission_type = db.Column(db.String(20), nullable=False)  # 'tuesday', 'friday'
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    feedback = db.Column(db.Text, nullable=True)
    feedback_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<WeeklySubmission {self.submission_id}>'