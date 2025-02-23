from flask import Blueprint, render_template
from app.utils.auth_utils import login_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/add_faculty')
@login_required(2)
def add_faculty():
    return render_template('admin/add_faculty.html')