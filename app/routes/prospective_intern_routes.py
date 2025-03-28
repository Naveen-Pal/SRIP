from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models.application import ApplicationForm
from app import db
from app.models.faculty import Faculty
from app.models.project import Project

bp = Blueprint('prospective_intern', __name__, url_prefix='/prospective_intern')

@bp.route('/application_form', methods=['GET', 'POST'])
def application_form():
    if request.method == 'POST':
        statement_of_purpose = request.form['statement_of_purpose']
        can_complete_internship = request.form.get('can_complete_internship') == 'yes'
        project_code = request.form['project_code']

        new_form = ApplicationForm(
            statement_of_purpose=statement_of_purpose,
            can_complete_internship=can_complete_internship,
            project_code=project_code
        )
        db.session.add(new_form)
        db.session.commit()
        return redirect(url_for('home.home'))
    
    result  = Faculty.query.with_entities(Faculty.faculty_id, Faculty.full_name).filter_by(allowed=1).all()
    faculties = [{"faculty_id": faculty_id, "name": full_name} for faculty_id, full_name in result]

    project_title = request.args.get("project_title", "")
    project_code = request.args.get("project_code", "")
    faculty = request.args.get("faculty", "")
    return render_template('intern/application_form.html',faculties=faculties,project_title=project_title, 
                           project_code=project_code, 
                           faculty=faculty)

@bp.route('/get_projects',methods=['GET'])
def get_projects():
    faculty_id = request.args.get('faculty_id')

    if not faculty_id:
        return jsonify({"error": "Missing faculty_id"}), 400
    projects = Project.query.with_entities(Project.project_id, Project.project_title).filter_by(faculty_id=faculty_id).all()

    # Convert to JSON format
    project_list = [{"project_id": p.project_id, "project_title": p.project_title} for p in projects]
    return jsonify({"projects": project_list}), 200


@bp.route('/projects', methods=['GET', 'POST'])
def projects():
    projects = Project.query.with_entities(Project.project_id, Project.project_title, Project.project_description, Project.faculty_id).all()

    project_list = sorted([{
        "project_id": p.project_id, 
        "project_title": p.project_title,
        "project_description": p.project_description,
        "faculty_id": p.faculty_id
    } for p in projects], key=lambda x: x["project_id"])
    
    return render_template('intern/projects.html', projects=project_list)

@bp.route('/<int:project_id>', methods=['GET', 'POST'])
def direct_apply(project_id):
    # project_id = request.view_args['id']
    # print(project_id)
    project = Project.query.get(project_id)
    print(project.faculty_id)
    faculty_name = Faculty.query.get(project.faculty_id).full_name
    project_title = project.project_title
    print(faculty_name)
    result  = Faculty.query.with_entities(Faculty.faculty_id, Faculty.full_name).filter_by(allowed=1).all()
    faculties = [{"faculty_id": faculty_id, "name": full_name} for faculty_id, full_name in result]
    return render_template('intern/application_form.html',faculty_id=project.faculty_id, faculty_name=faculty_name, project_title=project_title,project_id=project_id, faculties=faculties)

@bp.route('/status',methods =['GET'])
def status():
    return render_template('intern/dashboard.html')

