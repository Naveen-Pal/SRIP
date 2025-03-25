from flask import Blueprint, render_template, request, redirect, url_for, session,flash
from app.utils.auth_utils import hash_password, check_password
from app.models.faculty import Faculty
from app.models.coordinator import Coordinator
from app.models.selected_intern import SelectedIntern
from app.models.session import Session
from app import db
import uuid
import smtplib
import random


bp = Blueprint('auth', __name__, url_prefix='/auth')

# @bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         user_email = request.form['user_email']
#         user_pass = request.form['user_pass']
#         user_name = request.form['user_name']
        
#         hashed_password = hash_password(user_pass)

#         new_user = Faculty(
#             password=hashed_password,
#             email=user_email,
#             full_name=user_name,
#         )
            
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect('/')
#     return render_template('auth/register.html')

@bp.route('/intern', methods=['GET', 'POST'])
def login_intern():
    if request.method == 'POST':
        user_mail = request.form['user_mail']
        user_pass = request.form['user_pass']
        # user = User.query.filter_by(user_login=user_login).first()
        user = SelectedIntern.query.filter_by(email=user_mail).first()
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
            return render_template('intern/index.html')    
    return render_template('auth/login_intern.html')

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
            return redirect('faculty/add_project')
    return render_template('auth/login_faculty.html')

@bp.route('/coordinator', methods=['GET', 'POST'])
def login_coordinator():
    if request.method == 'POST':
        user_login = request.form['user_login']
        user_pass = request.form['user_pass']
        user = Coordinator.query.filter_by(email=user_login).first()
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
            return redirect('coordinator/faculty_approvement')
    return render_template('auth/login_coordinator.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')



# Function to send OTP via email
def send_otp(email, otp):
    sender_email = "your-email@example.com"
    sender_password = "your-email-password"
    subject = "Your OTP for Registration"
    message = f"Your OTP for registration is: {otp}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
        server.quit()
    except Exception as e:
        print("Error sending email:", e)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_email = request.form['user_email']
        user_pass = request.form['user_pass']
        user_name = request.form['user_name']

        # Generate and store OTP in session
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        session['user_data'] = {
            "email": user_email,
            "password": hash_password(user_pass),
            "name": user_name
        }

        send_otp(user_email, otp)

        # Render OTP verification page
        return render_template('auth/verify_otp.html', email=user_email)

    return render_template('auth/register.html')

@bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form['otp']

    if 'otp' in session and int(entered_otp) == session['otp']:
        user_data = session.pop('user_data', None)
        if user_data:
            new_user = Faculty(
                password=user_data['password'],
                email=user_data['email'],
                full_name=user_data['name']
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect('/')
    else:
        flash("Invalid OTP, please try again.", "danger")
        return redirect('/register')

    return redirect('/')