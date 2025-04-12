from flask import Blueprint, render_template
from app.utils.auth_utils import login_required
from app.utils.auth_middleware import role_required

bp = Blueprint('faculty', __name__, url_prefix='/faculty')


@bp.route('/add_project')
@role_required("faculty")
def add_project():
    return render_template('faculty/add_project.html')