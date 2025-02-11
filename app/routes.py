from flask import Blueprint, render_template, redirect, url_for, flash
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/register')
def register():
    return render_template('register.html')