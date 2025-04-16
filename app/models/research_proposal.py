from app.database import db
from datetime import datetime

class ResearchProposal(db.Model):
    proposal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    intern_id = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, nullable=False)
    faculty_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    proposal_content = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    feedback = db.Column(db.Text, nullable=True)
    feedback_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<ResearchProposal {self.proposal_id}>'