from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.models.user import User
import MySQLdb.cursors
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('home.html')

@auth_bp.route('/login')
def login():
    return render_template('login.html')
# application_form

@auth_bp.route('/application_form')
def application_form():
    return render_template('application_form.html')



@auth_bp.route('/get_projects')
def get_projects():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    faculty_id = request.args.get('faculty_id')
    cursor.execute("SELECT project_code, project_title FROM projects WHERE faculty_id = %s", (faculty_id,))
    projects = cursor.fetchall()
    cursor.close()
    # Convert the projects data to JSON format
    return jsonify({"projects": projects}), 200





@auth_bp.route('/register')
def register():
    return render_template('register.html')

