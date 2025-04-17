from flask import current_app, jsonify, redirect, request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, verify_jwt_in_request
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from app.config import Config

def check_password(hashed_password, password):
    """Verify if provided password matches hashed password"""
    try:
        # Add debugging
        result = check_password_hash(hashed_password, password)
        return result
    except Exception as e:
        return False

def generate_token(user_id, role):
    """Generate a JWT token with user ID and role"""
    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={"role": role},
        expires_delta = timedelta(days=1)  # Token expires in 1 day
    )
    return access_token

def hash_password(password):
    """Hash a password for secure storage"""
    return generate_password_hash(password)

def role_required(required_role):
    """Decorator to check if user has required role"""
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(locations=["cookies"])
                claims = get_jwt()
                user_role = claims.get("role")
                
                if user_role != required_role:
                    return redirect(f'/auth/{required_role}')
                
                return fn(*args, **kwargs)
            except Exception as e:
                return redirect(f'/auth/{required_role}')
        return wrapper
    return decorator
