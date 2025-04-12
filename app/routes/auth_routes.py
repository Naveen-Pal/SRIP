from flask import Blueprint, render_template,g, request, redirect, session,flash,jsonify,make_response
from app.utils.auth_utils import hash_password, check_password, send_otp
from app.models.faculty import Faculty
from app.models.coordinator import Coordinator
from app.models.intern import InternDetail
from app.models.session import Session
from app import db
import uuid
import random
from datetime import datetime
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity,get_jwt,set_access_cookies,unset_jwt_cookies



bp = Blueprint('auth', __name__, url_prefix='/auth')
def generate_token(user_id, role):
    print("Generating token for user_id:", user_id, "with role:", role)
    access_token = create_access_token(
        identity=str(user_id),  # identity must be a string/int
        additional_claims={"role": role},
        expires_delta=False
    )
    return access_token


@bp.route('/prospective_intern', methods=['GET', 'POST'])
def login_intern():
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        user = InternDetail.query.filter_by(email=user_mail,isSelected=0).first()
        if user and check_password(user.password, user_pass):
            session_id = str(uuid.uuid4())
            session['user_type'] = 0
            session['session_id'] = session_id
            new_session = Session(
                session_id=session_id,
                user_id=user.intern_id,
                user_type=0
            )
            db.session.add(new_session)
            db.session.commit()
            
            role = "prospective_intern"
            token = generate_token(user.intern_id, role)
            response = make_response(redirect('/prospective_intern/projects'))  # Redirect to intern dashboard
            set_access_cookies(response, token)  
            return response    

    return render_template('/auth/login_prospective_intern.html',error={"error":"Invalid Credentials"})

@bp.before_request
def decode_jwt():
    token = request.cookies.get('access_token_cookie')
    if token:
        try:
            payload = get_jwt(token)
            g.user = payload
        except Exception as e:
            g.user = None
    else:
        g.user = None
        
@bp.context_processor
def inject_user():
    return dict(user=g.user)

@bp.route('/selected_intern', methods=['GET', 'POST'])
def login_selected_intern():
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        user = InternDetail.query.filter_by(email=user_mail,isSelected=1).first()
        if user and check_password(user.password, user_pass):
            session_id = str(uuid.uuid4())
            session['user_type'] = 1
            session['session_id'] = session_id
            new_session = Session(
                session_id=session_id,
                user_id=user.intern_id,
                user_type=1
            )
            db.session.add(new_session)
            db.session.commit()
            
            role = "selected_intern"
            token = generate_token(user.intern_id, role)
            print("generating selected intern token successfully")
            response = make_response(redirect('/selected_intern/home'))
            set_access_cookies(response, token)  
            return response
    print("going to render login page for selected intern")
    return render_template('/auth/login_selected_intern.html',error={"error":"Invalid Credentials"})



@bp.route('/faculty', methods=['GET', 'POST'])
def login_faculty():
    if request.method == 'POST':
        email = request.form['email']
        user_pass = request.form['user_pass']
        user = Faculty.query.filter_by(email=email).first()
        if user and check_password(user.password, user_pass):
            session_id = str(uuid.uuid4())
            session['user_type'] = 1
            session['session_id'] = session_id
            new_session = Session(
                session_id=session_id,
                user_id=user.faculty_id,
                user_type=1
            )
            db.session.add(new_session)
            db.session.commit()
            
            role = "faculty"
            print("generating faculty token successfully")
            token = generate_token(user.faculty_id, role)
            response = make_response(redirect('/faculty/add_project'))  
            set_access_cookies(response, token)
            return response    
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
            token = generate_token(user.coordinator_id, "coordinator")
            response = make_response(redirect('/coordinator/faculty_approvement'))
            set_access_cookies(response, token) 
            return response
    return render_template('/auth/login_coordinator.html')

@bp.route('/logout')
def logout():
    response = make_response(redirect('/')) 
    session.pop('user_id', None)
    unset_jwt_cookies(response)
    return response

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
    user_type = request.args.get('type', 'prospective_intern')
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        raw_password = request.form['password']
        hashed_pw = hash_password(raw_password)

        if user_type == 'prospective_intern':
            new_user = InternDetail(
                intern_id=email,
                full_name=full_name,
                email=email,
                password=hashed_pw,
                isSelected=0
            )
        elif user_type == 'faculty':
            new_user = Faculty(
                email=email,
                full_name=full_name,
                password=hashed_pw
            )
        elif user_type == 'coordinator':
            new_user = Coordinator(
                email=email,
                full_name=full_name,
                password=hashed_pw
            )
        else:
            return "Invalid user type", 400

        db.session.add(new_user)
        db.session.commit()
        return redirect('/')

    return render_template(f'/auth/register_{user_type}.html')