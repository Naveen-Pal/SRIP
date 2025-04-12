from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
from app.utils.auth_utils import hash_password, check_password, send_otp
from app.models.faculty import Faculty
from app.models.coordinator import Coordinator
from app.models.intern import InternDetail
from app.models.session import Session
from app import db
import uuid
import random
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/intern', methods=['GET', 'POST'])
def login_intern():
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        user = InternDetail.query.filter_by(email=user_mail).first()
        
        if user and check_password(user.password, user_pass):
            session_id = str(uuid.uuid4())
            
            # Determine if user is a selected intern (type 0) or prospective intern (type 3)
            user_type = 4 if user.isSelected == 1 else 3
            session['user_type'] = user_type
            session['user_id'] = user.intern_id
            session['session_id'] = session_id
            
            new_session = Session(
                session_id=session_id,
                user_id=user.intern_id,
                user_type=user_type
            )
            db.session.add(new_session)
            db.session.commit()
            
            # Redirect based on user type
            if user_type == 4:
                return redirect('/selected_intern/')
            else:
                return redirect('/prospective_intern/projects')
        else:
            flash("Invalid credentials. Please try again.", "danger")
            
    return render_template('/auth/login_intern.html')

@bp.route('/faculty', methods=['GET', 'POST'])
def login_faculty():
    if request.method == 'POST':
        email = request.form['email']
        user_pass = request.form['user_pass']
        user = Faculty.query.filter_by(email=email).first()
        if user and check_password(user.password, user_pass):
            session_id = str(uuid.uuid4())
            session['user_type'] = 1
            session['user_id'] = user.faculty_id
            session['session_id'] = session_id
            new_session = Session(
                session_id=session_id,
                user_id=user.faculty_id,
                user_type=1
            )
            db.session.add(new_session)
            db.session.commit()
            return redirect('/faculty/')
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
            session['user_id'] = user.coordinator_id
            session['user_type'] = 2
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            new_session = Session(
                session_id=session_id,
                user_id=user.coordinator_id,
                user_type=2
            )
            db.session.add(new_session)
            db.session.commit()
            return redirect('/coordinator/')
        else:
            flash("Invalid credentials. Please try again.", "danger")
            
    return render_template('/auth/login_coordinator.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    entered_otp = data.get('otp', '')

    if 'otp' in session and entered_otp == session['otp']:
        user_data = session.pop('user_data', None)
        session.pop('otp', None)

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
                mobile = request.form['mobile'],
                email=email,
                nationality = request.form['nationality'],
                phone = request.form.get('phone'),
                alternate_email = request.form.get('alternate_email'),
                permanent_city = request.form['permanent_city'],
                date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
                degree = request.form['degree'],
                department = request.form['department'],
                college_name = request.form['college_name'],
                year_of_joining = int(request.form['year_of_joining']),
                college_city = request.form['college_city'],
                college_state = request.form['college_state'],
                college_country = request.form['college_country'],
                gpa_type = request.form['gpa_type'],
                gpa_value = float(request.form['gpa_value']),
                gender = request.form['gender'],
                isSelected = 0  # Set as prospective intern
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