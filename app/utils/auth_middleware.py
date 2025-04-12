from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from flask import request, jsonify, redirect, url_for

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(locations=["cookies"])  # Extract token from cookie
                claims = get_jwt()
                print("heyy i am checking the role")
                print(f"Claims: {claims}")
                print(f"Required Role: {required_role}")
                if claims.get("role") != required_role:
                    print(required_role,1)
                    return redirect(f'/auth/{required_role}')  # Redirect if role is incorrect
                print("heyy i am checking the role")
                
                return fn(*args, **kwargs)
            except Exception as e:
                print(f"[role_required] JWT error: {e}")
                return redirect(f'/auth/{required_role}')# Redirect if JWT is missing or invalid
        return wrapper
    return decorator
