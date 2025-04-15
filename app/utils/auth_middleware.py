from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from flask import  redirect

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(locations=["cookies"])  # Extract token from cookie
                claims = get_jwt()
                if claims.get("role") != required_role:
                    return redirect(f'/auth/{required_role}')  # Redirect if role is incorrect                
                return fn(*args, **kwargs)
            except Exception as e:
                return redirect(f'/auth/{required_role}')# Redirect if JWT is missing or invalid
        return wrapper
    return decorator
