from flask import Blueprint, render_template
from utils.auth_utils import login_required

bp = Blueprint('faculty', __name__, url_prefix="/faculty")

@bp.route('/add_project')
@login_required(1)
def add_project():
    return render_template('faculty/add_project.html')