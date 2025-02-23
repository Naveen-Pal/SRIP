from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.models.user import User
from app import db
from app.models.session import Session


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('home.html')

@auth_bp.route('/login')
def login():
    return render_template('login.html')
# application_form

@auth_bp.route('/application_form', methods=['GET', 'POST'])
def application_form():
    if request.method == 'POST':
        # Get all form fields
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
        college_city = request.form['city']
        college_state = request.form['state']
        college_country = request.form['country']
        gpa_type = request.form['gpa_type']
        gpa_value = request.form['gpa_value']
        gender = request.form['gender']
        statement_of_purpose = request.form['statement_of_purpose']
        can_complete_internship = request.form.get('can_complete_internship') == 'yes'
        faculty = request.form['faculty']
        project_code = request.form['project_code']
        
        # project_title = ""

        # cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # # Insert into database
        # cursor.execute('''
        #     INSERT INTO intern (
        #         full_name, mobile, nationality, phone, email, alternate_email,
        #         permanent_city, date_of_birth, degree, department, college_name,
        #         year_of_joining, college_city,college_state,college_country, gpa_type, gpa_value, gender,
        #         statement_of_purpose, can_complete_internship, faculty_id, project_code
        #     ) VALUES (
        #         %s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,
        #         %s, %s, %s, %s
        #     )
        # ''', (
        #     full_name, mobile, nationality, phone, email, alternate_email,
        #     permanent_city, date_of_birth, degree, department, college_name,
        #     year_of_joining, college_city,college_state,college_country, gpa_type, gpa_value, gender,
        #     statement_of_purpose, can_complete_internship, faculty, project_code
        # ))
        
        # db.connection.commit()
        # flash('Internship application submitted successfully!', 'success')
        # return redirect(url_for('home'))
        new_reg = 
        

    # GET request - display form
    session = 
    print("*****")
    query = "SELECT faculty_id, full_name FROM faculty WHERE allowed = 1"
    faculties = db.session.execute(query)
    print("*****")
    print(faculties)
    return render_template('application_form.html', faculties=faculties)




@auth_bp.route('/get_projects')
def get_projects():
    print("inside the request")
    # cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    faculty_id = request.args.get('faculty_id')
    # cursor.execute("SELECT project_code, project_title FROM projects WHERE faculty_id = %s", (faculty_id,))
    
    # projects = cursor.fetchall()
    query = "SELECT project_code, project_title FROM projects WHERE faculty_id = %s"
    projects = db.session.execute(query, (faculty_id,))
    print(projects)
    
    # cursor.close()
    # Convert the projects data to JSON format
    return jsonify({"projects": projects}), 200





@auth_bp.route('/register')
def register():
    return render_template('register.html')

