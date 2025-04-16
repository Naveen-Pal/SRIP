from database import db
from datetime import datetime

class MilestoneSubmission(db.Model):
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    intern_id = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, nullable=False)
    faculty_id = db.Column(db.Integer, nullable=False)
    submission_type = db.Column(db.String(20), nullable=False)  # 'midterm', 'pre_final'
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    document_path = db.Column(db.String(255), nullable=True)  # Path to uploaded document if any
    submission_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    remarks = db.Column(db.Text, nullable=True)
    review_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<MilestoneSubmission {self.submission_id}>'