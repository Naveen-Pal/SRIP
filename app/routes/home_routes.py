from flask import Blueprint, render_template
from app import db

bp = Blueprint('home', __name__)

@bp.route('/')
def home():
    return render_template('home.html')
