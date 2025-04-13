from datetime import datetime
import random
import uuid

from flask import Blueprint, flash, g, jsonify, make_response, redirect, render_template, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, set_access_cookies, unset_jwt_cookies

from app import db
from app.models.coordinator import Coordinator
from app.models.faculty import Faculty
from app.models.intern import InternDetail
from app.utils.auth_utils import check_password, generate_token, hash_password

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/prospective_intern', methods=['GET', 'POST'])
def login_prospective_intern():
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        user = InternDetail.query.filter_by(email=user_mail, isSelected=0).first()
        
        print(f"Login attempt for prospective intern: {user_mail}")
        if user:
            print(f"User found with ID: {user.intern_id}")
            if check_password(user.password, user_pass):
                print("Password check passed")
                token = generate_token(user.intern_id, "prospective_intern")
                response = make_response(redirect('/prospective_intern/projects'))
                set_access_cookies(response, token)
                return response
            else:
                print("Password check failed")
        else:
            print("User not found or not a prospective intern")
            
        flash("Invalid credentials or you are not registered as a prospective intern.", "danger")

    # Use the login_intern.html template with an intern_type parameter
    return render_template('/auth/login_prospective_intern.html', intern_type='prospective')

@bp.route('/selected_intern', methods=['GET', 'POST'])
def login_selected_intern():
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        user = InternDetail.query.filter_by(email=user_mail, isSelected=1).first()
        
        print(f"Login attempt for selected intern: {user_mail}")
        if user:
            print(f"User found with ID: {user.intern_id}")
            if check_password(user.password, user_pass):
                print("Password check passed")
                token = generate_token(user.intern_id, "selected_intern")
                response = make_response(redirect('/selected_intern/'))
                set_access_cookies(response, token)
                return response
            else:
                print("Password check failed")
        else:
            print("User not found or not a selected intern")
            
        flash("Invalid credentials or you are not registered as a selected intern.", "danger")

    # Use the login_intern.html template with an intern_type parameter
    return render_template('/auth/login_selected_intern.html', intern_type='selected')

@bp.route('/intern', methods=['GET', 'POST'])
def login_intern():
    """General intern login that determines type automatically"""
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        user = InternDetail.query.filter_by(email=user_mail).first()
        
        print(f"General login attempt for: {user_mail}")
        if user:
            print(f"User found with ID: {user.intern_id}, isSelected: {user.isSelected}")
            if check_password(user.password, user_pass):
                print("Password check passed")
                if user.isSelected == 1:
                    role = "selected_intern"
                    redirect_url = '/selected_intern/'
                else:
                    role = "prospective_intern"
                    redirect_url = '/prospective_intern/projects'
                    
                token = generate_token(user.intern_id, role)
                response = make_response(redirect(redirect_url))
                set_access_cookies(response, token)
                return response
            else:
                print("Password check failed")
        else:
            print("User not found")
            
        flash("Invalid credentials. Please try again.", "danger")

    return render_template('/auth/login_selected_intern.html')

@bp.route('/faculty', methods=['GET', 'POST'])
def login_faculty():
    if request.method == 'POST':
        email = request.form['email']
        user_pass = request.form['user_pass']
        user = Faculty.query.filter_by(email=email).first()
        if user and check_password(user.password, user_pass):
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

@bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    entered_otp = data.get('otp', '')
    stored_otp = request.cookies.get('otp')
    user_data = request.cookies.get('user_data')

    if stored_otp and entered_otp == stored_otp:
        if user_data:
            role = user_data.get('role')
            # Determine which model to use based on role
            if role == 1:
                new_user = Faculty(
                    password=user_data['password'],
                    email=user_data['email'],
                    full_name=user_data['name']
                )
            elif role == 2:
                new_user = Coordinator(
                    password=user_data['password'],
                    email=user_data['email'],
                    full_name=user_data['name']
                )
            elif role == 3:
                new_user = InternDetail(
                    password=user_data['password'],
                    email=user_data['email'],
                    full_name=user_data['name'],
                    isSelected=0
                )
            elif role == 0:
                new_user = InternDetail(
                    password=user_data['password'],
                    email=user_data['email'],
                    full_name=user_data['name'],
                    isSelected=1
                )
            else:
                return jsonify({"success": False, "message": "Invalid role"})

            db.session.add(new_user)
            db.session.commit()
            return jsonify({"success": True})

    return jsonify({"success": False, "message": "Invalid OTP"})

@bp.route('/register', methods=['GET', 'POST'])
def register():
    user_type = request.args.get('type', 'intern')
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        raw_password = request.form['password']
        hashed_pw = hash_password(raw_password)
        if user_type == 'intern':
            # Check if intern already exists
            existing_intern = InternDetail.query.filter_by(email=email).first()
            if existing_intern:
                flash("An account with this email already exists.", "danger")
                return render_template(f'/auth/register_{user_type}.html')
                
            # By default, register as prospective intern (isSelected=0)
            new_user = InternDetail(
                password=hashed_pw,
                full_name=full_name,
                mobile=request.form['mobile'],
                email=email,
                nationality=request.form['nationality'],
                phone=request.form.get('phone'),
                alternate_email=request.form.get('alternate_email'),
                permanent_city=request.form['permanent_city'],
                date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
                degree=request.form['degree'],
                department=request.form['department'],
                college_name=request.form['college_name'],
                year_of_joining=int(request.form['year_of_joining']),
                college_city=request.form['college_city'],
                college_state=request.form['college_state'],
                college_country=request.form['college_country'],
                gpa_type=request.form['gpa_type'],
                gpa_value=float(request.form['gpa_value']),
                gender=request.form['gender'],
                isSelected=0  # Set as prospective intern
            )
        elif user_type == 'faculty':
            # Check if faculty already exists
            existing_faculty = Faculty.query.filter_by(email=email).first()
            if existing_faculty:
                flash("An account with this email already exists.", "danger")
                return render_template(f'/auth/register_{user_type}.html')
                
            new_user = Faculty(
                email=email,
                full_name=full_name,
                password=hashed_pw
            )
        elif user_type == 'coordinator':
            # Check if coordinator already exists
            existing_coord = Coordinator.query.filter_by(email=email).first()
            if existing_coord:
                flash("An account with this email already exists.", "danger")
                return render_template(f'/auth/register_{user_type}.html')
                
            new_user = Coordinator(
                email=email,
                full_name=full_name,
                password=hashed_pw
            )
        else:
            flash("Invalid user type", "danger")
            return redirect('/')

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(f'/auth/{user_type}')

    return render_template(f'/auth/register_{user_type}.html')

@bp.before_request
def decode_jwt():
    token = request.cookies.get('access_token_cookie')
    if token:
        try:
            payload = get_jwt()
            g.user = payload
            
            # Extract role from JWT claims and set user_type
            role = payload.get('role', '')
            
            if role == 'faculty':
                g.user_type = 1
            elif role == 'coordinator':
                g.user_type = 2
            elif role == 'prospective_intern':
                g.user_type = 3
            elif role == 'selected_intern':
                g.user_type = 4
            else:
                g.user_type = None
                
            # Also store the user's identity (ID)
            g.user_id = get_jwt_identity()
                
            # Fetch the actual user object for template use
            if g.user_type == 1:
                g.user_obj = Faculty.query.get(g.user_id)
            elif g.user_type == 2:
                g.user_obj = Coordinator.query.get(g.user_id)
            elif g.user_type in [3, 4]:
                g.user_obj = InternDetail.query.get(g.user_id)
            else:
                g.user_obj = None
                
        except Exception as e:
            print(f"JWT decode error: {e}")
            g.user = None
            g.user_type = None
            g.user_id = None
            g.user_obj = None
    else:
        g.user = None
        g.user_type = None
        g.user_id = None
        g.user_obj = None

@bp.context_processor
def inject_user():
    return dict(user=g.user, user_type=g.user_type, user_id=g.user_id, user_obj=g.user_obj)