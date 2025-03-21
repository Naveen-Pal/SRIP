from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for, session
from functools import wraps
from app.utils.session_utils import verify_session

def hash_password(password):
    return generate_password_hash(password)

def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

def login_required(user_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_id = session.get('session_id')
            if not user_type or not session_id or not verify_session(session_id, user_type):
                if (user_type == 1):
                    return redirect('/auth/faculty')
                elif (user_type == 2):
                    return redirect('/auth/coordinator')
                elif (user_type == 0):
                    return redirect('/auth/intern')
                else:
                    return redirect('/')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
