from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.auth_utils import login_required
from app.models.faculty import Faculty
from app import db
from app.utils.auth_middleware import role_required


bp = Blueprint('coordinator', __name__, url_prefix='/coordinator')

@bp.route('/email_selected_interns')
@role_required('coordinator')
def email_selected_interns():
    return render_template('coordinator/email_selected_interns.html')

@bp.route('/add_faculty')
@role_required('coordinator')
def add_faculty():
    return render_template('coordinator/add_faculty.html')

@bp.route('/faculty_approvement', methods=['GET', 'POST'])
@role_required('coordinator')
def faculty_approvement():
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            faculty_id = request.form.get('faculty_id')
            faculty = Faculty.query.get(faculty_id)
            
            if not faculty:
                return "Faculty not found", 404
            
            if action == 'toggle':
                faculty.allowed = 1 if faculty.allowed == 0 else 0
                db.session.commit()
            elif action == 'delete':
                db.session.delete(faculty)
                db.session.commit()
            return redirect('/coordinator/faculty_approvement')
        
        filter_type = request.args.get('filter', 'all')
        if filter_type == 'allowed':
            faculties = Faculty.query.filter_by(allowed=1).all()
        elif filter_type == 'unallowed':
            faculties = Faculty.query.filter_by(allowed=0).all()
        else:
            faculties = Faculty.query.all()
        return render_template('coordinator/faculty_approvement.html', faculties=faculties, filter_type=filter_type)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500