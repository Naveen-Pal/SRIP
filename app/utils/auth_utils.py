from flask import current_app, jsonify, redirect, request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, verify_jwt_in_request
from functools import wraps
import smtplib
from werkzeug.security import check_password_hash, generate_password_hash

from app.config import Config

def check_password(hashed_password, password):
    """Verify if provided password matches hashed password"""
    try:
        # Add debugging
        print(f"Checking password (hashed length: {len(hashed_password) if hashed_password else 'None'})")
        result = check_password_hash(hashed_password, password)
        print(f"Password check result: {result}")
        return result
    except Exception as e:
        print(f"Password check error: {str(e)}")
        return False

def generate_token(user_id, role):
    """Generate a JWT token with user ID and role"""
    access_token = create_access_token(
        identity=str(user_id),
        additional_claims={"role": role}
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
                # First verify the JWT is valid
                verify_jwt_in_request(locations=["cookies"])
                
                # Then get the JWT claims
                claims = get_jwt()
                
                # Log for debugging
                print(f"JWT Claims: {claims}")
                print(f"Required role: {required_role}")
                
                # Check if role matches
                user_role = claims.get("role")
                print(f"User role from token: {user_role}")
                
                if user_role != required_role:
                    print(f"Role mismatch: {user_role} != {required_role}")
                    return redirect(f'/auth/{required_role}')
                
                print("Role check passed!")
                return fn(*args, **kwargs)
            except Exception as e:
                print(f"JWT Authentication Error: {str(e)}")
                # Check if there's a token at all
                token = request.cookies.get('access_token_cookie')
                if token:
                    print("Token exists but is invalid")
                else:
                    print("No token found in cookies")
                return redirect(f'/auth/{required_role}')
        return wrapper
    return decorator

def send_otp(email, otp):
    """Send OTP via email"""
    sender_email = Config.MAIL_USERNAME
    sender_password = Config.MAIL_PASSWORD
    subject = "Your OTP for Registration"
    message = f"Your OTP for registration is: {otp}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
        server.quit()
    except Exception as e:
        raise Exception(f"Failed to send OTP: {str(e)}")