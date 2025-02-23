from flask import Blueprint, render_template
from app.utils.auth_utils import login_required

bp = Blueprint('coordinator', __name__, url_prefix='/coordinator')

@bp.route('/email_selected_interns')
@login_required(2)
def email_selected_interns():
    return render_template('coordinator/email_selected_interns.html')