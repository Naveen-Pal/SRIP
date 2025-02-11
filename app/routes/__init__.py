from flask import Blueprint

bp = Blueprint('routes', __name__)

from . import admin_routes, faculty_routes, intern_routes, coordinator_routes, auth_routes, home_routes