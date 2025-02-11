from flask import Blueprint, render_template, request, redirect, url_for, session
from app.utils.auth_utils import hash_password, check_password
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_login = request.form['user_login']
        user_pass = request.form['user_pass']
        user = User.query.filter_by(user_login=user_login).first()
        if user and check_password(user.user_pass, user_pass):
            session['user_id'] = user.id
            return redirect(url_for('home.home'))
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_login = request.form['user_login']
        user_pass = request.form['user_pass']
        user_nicename = request.form['user_nicename']
        user_email = request.form['user_email']
        hashed_password = hash_password(user_pass)
        new_user = User(
            user_login=user_login,
            user_pass=hashed_password,
            user_nicename=user_nicename,
            user_email=user_email,
            display_name=user_nicename
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('home.home'))
    return render_template('auth/register.html')