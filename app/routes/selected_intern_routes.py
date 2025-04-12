from flask import Blueprint, render_template #, request, redirect, url_for,jsonify
# from app.models.intern import Intern
# from app import db
# from app.models.faculty import Faculty
# from app.models import Project 


bp = Blueprint('selected_intern', __name__, url_prefix='/selected_intern')

from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity,get_jwt
from app.utils.auth_middleware import role_required
@jwt_required()  # Extracts JWT from cookie
@bp.route('/home', methods=['GET'])
@role_required("selected_intern")
def home():
    return render_template('intern/index.html')
