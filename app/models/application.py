from app import db

class ApplicationForm(db.Model):
    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    intern_id = db.Column(db.String(50), nullable=False)
    statement_of_purpose = db.Column(db.Text, nullable=False)
    faculty = db.Column(db.String(500), nullable=False)
    project_code = db.Column(db.String(10), nullable=False)
    can_complete_internship = db.Column(db.Boolean, nullable=False, default=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    time_stamp_modified = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())