from datetime import datetime,timedelta
import random
from flask import Blueprint, flash, g, jsonify, make_response, redirect, render_template, request,session
from flask_jwt_extended import get_jwt, get_jwt_identity, set_access_cookies, unset_jwt_cookies,verify_jwt_in_request
from app import db
from app.models.coordinator import Coordinator
from app.models.faculty import Faculty
from app.models.intern import InternDetail
from app.utils.auth_utils import check_password, generate_token, hash_password
from app.utils.email_utils import send_email
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/prospective_intern', methods=['GET', 'POST'])
def login_prospective_intern():
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        user = InternDetail.query.filter_by(email=user_mail, isSelected=0).first()
        
        if user:
            if check_password(user.password, user_pass):
                token = generate_token(user.intern_id, "prospective_intern")
                response = make_response(redirect('/prospective_intern/projects'))
                set_access_cookies(response, token)
                return response
            
        flash("Invalid credentials or you are not registered as a prospective intern.", "danger")

    # Use the login_intern.html template with an intern_type parameter
    return render_template('/auth/login_prospective_intern.html', intern_type='prospective')

@bp.route('/selected_intern', methods=['GET', 'POST'])
def login_selected_intern():
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        user = InternDetail.query.filter_by(email=user_mail, isSelected=1).first()
        
        if user:
            if check_password(user.password, user_pass):
                token = generate_token(user.intern_id, "selected_intern")
                response = make_response(redirect('/selected_intern/'))
                set_access_cookies(response, token)
                return response
            
        flash("Invalid credentials or you are not registered as a selected intern.", "danger")

    # Use the login_intern.html template with an intern_type parameter
    return render_template('/auth/login_selected_intern.html', intern_type='selected')


@bp.route('/faculty', methods=['GET', 'POST'])
def login_faculty():
    if request.method == 'POST':
        email = request.form['email']
        user_pass = request.form['user_pass']
        user = Faculty.query.filter_by(email=email).first()
        if user and check_password(user.password, user_pass) and user.isSelected == 1:
            token = generate_token(user.faculty_id, "faculty")
            response = make_response(redirect('/faculty/'))  
            set_access_cookies(response, token)
            return response
        else:
            flash("Invalid credentials. Please try again.", "danger")
            
    return render_template('/auth/login_faculty.html')

@bp.route('/coordinator', methods=['GET', 'POST'])
def login_coordinator():
    if request.method == 'POST':
        user_email = request.form['user_email']
        user_pass = request.form['user_pass']
        user = Coordinator.query.filter_by(email=user_email).first()
        if user and check_password(user.password, user_pass):
            token = generate_token(user.coordinator_id, "coordinator")
            response = make_response(redirect('/coordinator/'))
            set_access_cookies(response, token) 
            return response
        else:
            flash("Invalid credentials. Please try again.", "danger")
            
    return render_template('/auth/login_coordinator.html')

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    response = make_response(redirect('/'))
    unset_jwt_cookies(response)
    return response


@bp.route('/register', methods=['GET', 'POST'])
def register():
    user_type = request.args.get('type', 'intern')
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        raw_password = request.form['password']
        
        # Check for existing user before sending OTP
        if user_type == 'intern':
            if InternDetail.query.filter_by(email=email).first():
                flash("An account with this email already exists.", "danger")
                return render_template(f'/auth/register_{user_type}.html')
        elif user_type == 'faculty':
            if Faculty.query.filter_by(email=email).first():
                flash("An account with this email already exists.", "danger")
                return render_template(f'/auth/register_{user_type}.html')
        elif user_type == 'coordinator':
            if Coordinator.query.filter_by(email=email).first():
                flash("An account with this email already exists.", "danger")
                return render_template(f'/auth/register_{user_type}.html')

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Store all form data and OTP in session temporarily
        session['registration_data'] = request.form.to_dict()
        session['otp'] = otp
        session['user_type'] = user_type

        # Send OTP via email
        subject = "Your OTP for Registration"
        message = f"Your OTP for registration is: {otp}"
        recipients = [email]
        send_email(subject, recipients, message)

        flash("An OTP has been sent to your email. Please verify to complete registration.", "info")
        return render_template('/auth/verify_otp.html')

    return render_template(f'/auth/register_{user_type}.html')
@bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    print(request.json)
    entered_otp = request.json.get('otp')
    actual_otp = session.get('otp')
    data = session.get('registration_data')
    user_type = session.get('user_type')
    print("Entered OTP:", entered_otp)
    print("Actual OTP:", actual_otp)
    print("User Type:", user_type)
    print("Registration Data:", data)
    if entered_otp != actual_otp:
        flash("Invalid OTP", "danger")
        return jsonify({"success": False, "message": "Invalid OTP"})

    hashed_pw = hash_password(data['password'])

    if user_type == 'intern':
        new_user = InternDetail(
            email=data['email'],
            full_name=data['full_name'],
            password=hashed_pw,
            mobile=data['mobile'],
            nationality=data['nationality'],
            phone=data.get('phone'),
            alternate_email=data.get('alternate_email'),
            permanent_city=data['permanent_city'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            degree=data['degree'],
            department=data['department'],
            college_name=data['college_name'],
            year_of_joining=int(data['year_of_joining']),
            college_city=data['college_city'],
            college_state=data['college_state'],
            college_country=data['college_country'],
            gpa_type=data['gpa_type'],
            gpa_value=float(data['gpa_value']),
            gender=data['gender'],
            isSelected=0
        )
    elif user_type == 'faculty':
        new_user = Faculty(
            email=data['email'],
            full_name=data['full_name'],
            password=hashed_pw
        )
        print("Faculty Registration Data:", data)
    elif user_type == 'coordinator':
        new_user = Coordinator(
            email=data['email'],
            full_name=data['full_name'],
            password=hashed_pw
        )

    db.session.add(new_user)
    db.session.commit()
    session.clear()
    print("User registered successfully")
    flash("Registration successful!", "success")
    return jsonify({"success": True, "redirect": f"/auth/{user_type}"})

@bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = session.get('registration_data')
    if not data: return "Session expired", 400

    new_otp = str(random.randint(100000, 999999))
    session['otp'] = new_otp
    subject = "Your OTP for Registration"
    message = f"Your OTP for registration is: {new_otp}"
    recipient = data['email']
    send_email(subject, recipient, message)
    return "OK", 200


@bp.before_app_request
def decode_jwt():
    # Check if the JWT is valid and extract user information
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        role = get_jwt()["role"]
        g.user_id = identity
        g.user_type = role

        if role == "faculty":
            g.user_obj = Faculty.query.get(identity)
        elif role == "coordinator":
            g.user_obj = Coordinator.query.get(identity)
        elif role == "selected_intern":
            g.user_obj = InternDetail.query.get(identity)
        else:
            g.user_obj = None

    except Exception as e:
        g.user_id = None
        g.user_type = None
        g.user_obj = None
@bp.app_context_processor
def inject_user():
    """Inject user information into templates"""
    return dict(
        user=getattr(g, "user", None),
        user_id=getattr(g, "user_id", None),
        user_type=getattr(g, "user_type", None),
        user_obj=getattr(g, "user_obj", None)
    )

    
