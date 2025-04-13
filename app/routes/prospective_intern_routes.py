from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_jwt_extended import get_jwt_identity

from app.models.application import ApplicationForm
from app.models.intern import InternDetail
from app import db
from app.models.faculty import Faculty
from app.models.project import Project
from app.utils.auth_utils import role_required

bp = Blueprint('prospective_intern', __name__, url_prefix='/prospective_intern')

@bp.route('/projects', methods=['GET'])
def projects():
    print("inside projects")
    projects = Project.query.with_entities(Project.project_id, Project.project_title, Project.project_description, Project.faculty_id).all()
    
    project_list = []
    for p in projects:
        faculty = Faculty.query.get(p.faculty_id)
        faculty_name = faculty.full_name if faculty else "Unknown"
        project_list.append({
            "project_id": p.project_id, 
            "project_title": p.project_title,
            "project_description": p.project_description,
            "faculty_name": faculty_name,
            "faculty_id": p.faculty_id
        })
    
    project_list = sorted(project_list, key=lambda x: x["project_id"])
    
    return render_template('intern/projects.html', projects=project_list)

@bp.route('/my_applications', methods=['GET'])
@role_required('prospective_intern')
def my_applications():
    intern_id = get_jwt_identity()
    
    # Get all applications by this intern with project and faculty details
    applications = db.session.query(ApplicationForm, Project, Faculty)\
        .join(Project, Project.project_id == ApplicationForm.project_code)\
        .join(Faculty, Faculty.faculty_id == Project.faculty_id)\
        .filter(ApplicationForm.intern_id == intern_id)\
        .all()
    
    # Format the data for the template
    application_list = []
    for app, project, faculty in applications:
        application_list.append({
            'application_id': app.application_id,
            'project_code': app.project_code,
            'project_title': project.project_title,
            'faculty_name': faculty.full_name,
            'status': app.status,
            'time_stamp': app.time_stamp,
            'faculty_feedback': app.faculty_feedback
        })
        
    return render_template('intern/applied_projects.html', applications=application_list)

@bp.route('/status', methods=['GET'])
@role_required('prospective_intern')  # User type 3 for prospective interns
def status():
    return redirect('/prospective_intern/my_applications')

@bp.route('/submit_application', methods=['POST'])
@role_required('prospective_intern')
def submit_application():
    """AJAX endpoint for submitting project applications."""
    intern_id = get_jwt_identity()
    if not intern_id:
        return jsonify({
            'success': False,
            'message': 'You must be logged in to apply for projects'
        }), 401
    
    try:
        statement_of_purpose = request.form.get('statement_of_purpose')
        can_complete_internship = request.form.get('can_complete_internship') == 'yes'
        project_code = int(request.form.get('project_code'))
        faculty_id = request.form.get('faculty')
        
        # Validate form data
        if not statement_of_purpose or not project_code or not faculty_id:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Check if already applied to this project
        existing_application = ApplicationForm.query.filter_by(
            intern_id=intern_id, 
            project_code=project_code
        ).first()
        
        if existing_application:
            return jsonify({
                'success': False,
                'message': 'You have already applied for this project'
            }), 400
        
        # Create new application
        new_form = ApplicationForm(
            intern_id=intern_id,
            statement_of_purpose=statement_of_purpose,
            can_complete_internship=can_complete_internship,
            project_code=project_code,
            faculty=faculty_id,
            status='pending'
        )
        
        db.session.add(new_form)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application submitted successfully!',
            'redirect': '/prospective_intern/my_applications'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting application: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while submitting your application'
        }), 500

