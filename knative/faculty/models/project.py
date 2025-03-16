from app import db

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_title = db.Column(db.String(500), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    number_of_student = db.Column(db.Integer, nullable=False)
    faculty_email = db.Column(db.String(50), nullable=False)
    faculty_id = db.Column(db.Integer,nullable=False)
    project_mode = db.Column(db.String(50), nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())