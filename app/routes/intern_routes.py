from flask import Blueprint, render_template, request, redirect, url_for,jsonify
from app.models.intern import Intern
from app import db
from app.models.faculty import Faculty
from app.models import Project 


bp = Blueprint('intern', __name__, url_prefix='/intern')

@bp.route('/application_form', methods=['GET', 'POST'])
def application_form():
    if request.method == 'POST':
        full_name = request.form['full_name']
        mobile = request.form['mobile']
        nationality = request.form['nationality']
        phone = request.form['phone']
        email = request.form['email']
        alternate_email = request.form['alternate_email']
        permanent_city = request.form['permanent_city']
        date_of_birth = request.form['date_of_birth']
        degree = request.form['degree']
        department = request.form['department']
        college_name = request.form['college_name']
        year_of_joining = request.form['year_of_joining']
        college_city = request.form['college_city']
        college_state = request.form['college_state']
        college_country = request.form['college_country']
        gpa_type = request.form['gpa_type']
        gpa_value = request.form['gpa_value']
        gender = request.form['gender']
        statement_of_purpose = request.form['statement_of_purpose']
        can_complete_internship = request.form.get('can_complete_internship') == 'yes'
        faculty = request.form['faculty']
        project_code = request.form['project_code']

        new_intern = Intern(
            intern_id=email,
            full_name=full_name,
            mobile=mobile,
            nationality=nationality,
            phone=phone,
            email=email,
            alternate_email=alternate_email,
            permanent_city=permanent_city,
            date_of_birth=date_of_birth,
            degree=degree,
            department=department,
            college_name=college_name,
            year_of_joining=year_of_joining,
            college_city=college_city,
            college_state=college_state,
            college_country=college_country,
            gpa_type=gpa_type,
            gpa_value=gpa_value,
            gender=gender,
            statement_of_purpose=statement_of_purpose,
            can_complete_internship=can_complete_internship,
            faculty=faculty,
            project_code=project_code
        )
        db.session.add(new_intern)
        db.session.commit()
        return redirect(url_for('home.home'))
    
    result  = Faculty.query.with_entities(Faculty.faculty_id, Faculty.full_name).filter_by(allowed=1).all()
    faculties = [{"faculty_id": faculty_id, "name": full_name} for faculty_id, full_name in result]

    project_title = request.args.get("project_title", "")
    project_code = request.args.get("project_code", "")
    faculty = request.args.get("faculty", "")
    print("goint to application form with "+project_code+project_title)
    return render_template('intern/application_form.html',faculties=faculties,project_title=project_title, 
                           project_code=project_code, 
                           faculty=faculty)

@bp.route('/get_projects',methods=['GET'])
def get_projects():
    faculty_id = request.args.get('faculty_id')

    if not faculty_id:
        return jsonify({"error": "Missing faculty_id"}), 400
    print(faculty_id)
    projects = Project.query.with_entities(Project.project_id, Project.project_title).filter_by(faculty_id=faculty_id).all()

    # Convert to JSON format
    project_list = [{"project_id": p.project_id, "project_title": p.project_title} for p in projects]
    print(project_list)
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

@bp.route('/home', methods=['POST'])
def home():
    return render_template('intern/index.html')
