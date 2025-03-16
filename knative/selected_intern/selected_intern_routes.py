from flask import Blueprint, render_template #, request, redirect, url_for,jsonify
# from app.models.intern import Intern
# from app import db
# from app.models.faculty import Faculty
# from app.models import Project 


bp = Blueprint('selected_intern', __name__, url_prefix='/selected_intern')

@bp.route('/home', methods=['GET'])
def home():
    return render_template('intern/index.html')