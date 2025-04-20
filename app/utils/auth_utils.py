from flask import current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
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
                # Use optional=True to check if token exists but not raise an exception if it doesn't
                verify_jwt_in_request(locations=["cookies"], optional=True)
                
                # Check if user is authenticated
                identity = get_jwt_identity()
                
                # If no identity, user is not logged in
                if not identity:
                    return redirect(f'/auth/{required_role}')
                
                claims = get_jwt()
                user_role = claims.get("role")
                
                # Check if user has the correct role
                if user_role != required_role:
                    # If user has a different role, redirect to the correct area
                    if user_role == "faculty":
                        return redirect('/faculty/')
                    elif user_role == "coordinator":
                        return redirect('/coordinator/')
                    elif user_role == "prospective_intern":
                        return redirect('/prospective_intern/projects')
                    elif user_role == "selected_intern":
                        return redirect('/selected_intern/')
                    else:
                        # If role doesn't match, redirect to login
                        return redirect(f'/auth/{required_role}')
                
                return fn(*args, **kwargs)
            except Exception as e:
                # Log the error for debugging
                print(f"Authentication error: {str(e)}")
                return redirect(f'/auth/{required_role}')
        return wrapper
    return decorator
