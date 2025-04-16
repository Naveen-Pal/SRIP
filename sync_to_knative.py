#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

def sync_common_folders(source_root, target_root, folder_name):
    """Sync common folders like models, utils, static"""
    source_dir = os.path.join(source_root, folder_name)
    if not os.path.exists(source_dir):
        print(f"Warning: {source_dir} does not exist")
        return
        
    for service_dir in os.listdir(target_root):
        service_path = os.path.join(target_root, service_dir)
        if os.path.isdir(service_path) and not service_dir.startswith('.'):
            target_dir = os.path.join(service_path, folder_name)
            
            # Create target directory if it doesn't exist
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            # Remove existing files in target directory
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path) and item != '__pycache__':
                    shutil.rmtree(item_path)
            
            # Copy from source to target
            for item in os.listdir(source_dir):
                if item == '__pycache__':
                    continue
                    
                source_item = os.path.join(source_dir, item)
                target_item = os.path.join(target_dir, item)
                
                if os.path.isfile(source_item):
                    shutil.copy2(source_item, target_item)
                elif os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                    
            print(f"Synced {folder_name} to {service_dir}")

def sync_service_specific_files(source_root, target_root):
    """Sync service-specific routes and templates"""
    services = {
        'auth': 'auth_routes.py',
        'coordinator': 'coordinator_routes.py',
        'faculty': 'faculty_routes.py',
        'home': 'home_routes.py',
        'prospective_intern': 'prospective_intern_routes.py',
        'selected_intern': 'selected_intern_routes.py'
    }
    
    for service_name, route_file in services.items():
        # Check if service directory exists in knative
        service_dir = os.path.join(target_root, service_name)
        if not os.path.exists(service_dir):
            print(f"Warning: Service directory {service_dir} does not exist")
            continue
        
        # Copy route file
        source_route = os.path.join(source_root, 'app', 'routes', route_file)
        target_route = os.path.join(service_dir, route_file)
        
        if os.path.exists(source_route):
            shutil.copy2(source_route, target_route)
            print(f"Copied {route_file} to {service_name} service")
        else:
            print(f"Warning: Source route file {source_route} does not exist")
            
        # Sync relevant templates
        sync_service_templates(source_root, service_name, service_dir)

def sync_service_templates(source_root, service_name, service_dir):
    """Sync templates relevant to specific service"""
    source_templates = os.path.join(source_root, 'app', 'templates')
    target_templates = os.path.join(service_dir, 'templates')

    # Ensure target templates directory exists
    if not os.path.exists(target_templates):
        os.makedirs(target_templates)

    # Remove existing files in target templates directory
    for item in os.listdir(target_templates):
        item_path = os.path.join(target_templates, item)
        if os.path.isfile(item_path):
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

    # Copy common templates (base, header, footer, etc.)
    for item in os.listdir(source_templates):
        source_path = os.path.join(source_templates, item)
        target_path = os.path.join(target_templates, item)

        if os.path.isfile(source_path):
            shutil.copy2(source_path, target_path)
        # Copy specific template directories for all services (auth, etc.)
        elif os.path.isdir(source_path) and item == 'auth':
            # Auth templates are needed by all services for login
            shutil.copytree(source_path, target_path, dirs_exist_ok=True)

    # Copy service-specific templates
    service_mapping = {
        'auth': ['auth'],
        'coordinator': ['coordinator'],
        'faculty': ['faculty'],
        'home': [],  # Home only needs base templates
        'prospective_intern': ['intern'],
        'selected_intern': ['intern']
    }
    
    for folder in service_mapping.get(service_name, []):
        folder_path = os.path.join(source_templates, folder)
        if os.path.exists(folder_path):
            target_folder = os.path.join(target_templates, folder)
            shutil.copytree(folder_path, target_folder, dirs_exist_ok=True)
            print(f"  - Copied {folder} templates")

    print(f"Copied templates for {service_name} service")

def update_app_files(source_root, target_root):
    """Update the app.py, config.py, and database.py for each service"""
    for service_dir in os.listdir(target_root):
        service_path = os.path.join(target_root, service_dir)
        if not os.path.isdir(service_path) or service_dir.startswith('.'):
            continue
            
        # Copy config.py from main app to service
        source_config = os.path.join(source_root, 'app', 'config.py')
        target_config = os.path.join(service_path, 'config.py')
        if os.path.exists(source_config):
            shutil.copy2(source_config, target_config)
            print(f"Copied config.py to {service_dir} service")
            
        # Copy database.py from main app to service
        source_database = os.path.join(source_root, 'app', 'database.py')
        target_database = os.path.join(service_path, 'database.py')
        if os.path.exists(source_database):
            shutil.copy2(source_database, target_database)
            print(f"Copied database.py to {service_dir} service")
        
        # Update app.py for the service
        update_app_py_for_service(source_root, service_path, service_dir)

def update_app_py_for_service(source_root, service_path, service_name):
    """Update app.py for a specific service with proper imports and configurations"""
    route_file_name = ""
    if service_name == 'auth':
        route_file_name = 'auth_routes.py'
        blueprint_name = 'auth_routes.bp'
    elif service_name == 'coordinator':
        route_file_name = 'coordinator_routes.py'
        blueprint_name = 'coordinator_routes.bp'
    elif service_name == 'faculty':
        route_file_name = 'faculty_routes.py'
        blueprint_name = 'faculty_routes.bp'
    elif service_name == 'home':
        route_file_name = 'home_routes.py'
        blueprint_name = 'home_routes.bp'
    elif service_name == 'prospective_intern':
        route_file_name = 'prospective_intern_routes.py'
        blueprint_name = 'prospective_intern_routes.bp'
    elif service_name == 'selected_intern':
        route_file_name = 'selected_intern_routes.py'
        blueprint_name = 'selected_intern_routes.bp'
    else:
        print(f"Warning: Unknown service {service_name}, skipping app.py update")
        return
    
    app_py_content = f"""from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from config import Config
from database import db

# Import routes
import {route_file_name.replace('.py', '')}

jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Register blueprints
    app.register_blueprint({blueprint_name})
    
    # Setup JWT loader for user info
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user
        
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        role = jwt_data["role"]
        
        # Handle different user types
        if role == "faculty":
            from models.faculty import Faculty
            return Faculty.query.get(identity)
        elif role == "coordinator":
            from models.coordinator import Coordinator
            return Coordinator.query.get(identity)
        elif role in ["selected_intern", "prospective_intern"]:
            from models.intern import InternDetail
            return InternDetail.query.get(identity)
        
        return None
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
"""

    app_py_path = os.path.join(service_path, 'app.py')
    with open(app_py_path, 'w') as file:
        file.write(app_py_content)
    
    print(f"Updated app.py for {service_name} service")

def update_docker_files(target_root):
    """Update Dockerfile for each service"""
    for service_dir in os.listdir(target_root):
        service_path = os.path.join(target_root, service_dir)
        if not os.path.isdir(service_path) or service_dir.startswith('.'):
            continue
        
        # Create/update Dockerfile
        dockerfile_path = os.path.join(service_path, 'dockerfile')
        
        dockerfile_content = """FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
"""
        with open(dockerfile_path, 'w') as file:
            file.write(dockerfile_content)
        
        print(f"Updated Dockerfile for {service_dir} service")
        
        # Create/update requirements.txt
        update_requirements(service_path)

def update_requirements(service_path):
    """Update requirements.txt for each service"""
    requirements_content = """Flask
Flask-SQLAlchemy
Flask-Mail
python-dotenv
pymysql
flask_jwt_extended
gunicorn"""
    
    requirements_path = os.path.join(service_path, 'requirements.txt')
    with open(requirements_path, 'w') as file:
        file.write(requirements_content)
    
    print(f"Updated requirements.txt for {os.path.basename(service_path)} service")

def main():
    # Set paths
    source_root = os.path.dirname(os.path.abspath(__file__))  # Current script directory
    target_root = os.path.join(source_root, 'knative')
    
    if not os.path.exists(target_root):
        print(f"Error: Target directory {target_root} does not exist")
        sys.exit(1)
    
    # Sync common folders
    sync_common_folders(os.path.join(source_root, 'app'), target_root, 'models')
    sync_common_folders(os.path.join(source_root, 'app'), target_root, 'utils')
    sync_common_folders(os.path.join(source_root, 'app'), target_root, 'static')
    
    # Sync service-specific files
    sync_service_specific_files(source_root, target_root)
    
    # Update app.py and config.py files
    update_app_files(source_root, target_root)
    
    # Update Docker files
    update_docker_files(target_root)
    
    print("\nSync completed successfully. Docker containers can now be built for each service.")
    print("\nBuild instructions:")
    print("1. Navigate to each service directory in 'knative/'")
    print("2. Run: docker build -t ghcr.io/naveen-pal/srip-<service_name>:latest .")
    print("3. Push to GitHub Container Registry: docker push ghcr.io/naveen-pal/srip-<service_name>:latest")

if __name__ == "__main__":
    main()