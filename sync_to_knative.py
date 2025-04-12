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
        if os.path.isdir(service_path):
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
        
    # Copy common templates
    common_templates = ['base.html', 'header.html', 'footer.html', 'home.html']
    for template in common_templates:
        source_path = os.path.join(source_templates, template)
        if os.path.exists(source_path):
            shutil.copy2(source_path, os.path.join(target_templates, template))
            
    # Copy auth templates folder (needed by most services)
    source_auth = os.path.join(source_templates, 'auth')
    target_auth = os.path.join(target_templates, 'auth')
    if os.path.exists(source_auth):
        if os.path.exists(target_auth):
            shutil.rmtree(target_auth)
        shutil.copytree(source_auth, target_auth)
    
    # Copy service-specific templates
    if service_name in ['auth', 'coordinator', 'faculty', 'home', 'prospective_intern', 'selected_intern']:
        # Map 'prospective_intern' and 'selected_intern' to 'intern' template folder
        template_folder = 'intern' if service_name in ['prospective_intern', 'selected_intern'] else service_name
        
        source_specific = os.path.join(source_templates, template_folder)
        target_specific = os.path.join(target_templates, template_folder)
        
        if os.path.exists(source_specific):
            if os.path.exists(target_specific):
                shutil.rmtree(target_specific)
            shutil.copytree(source_specific, target_specific)
            print(f"Copied templates for {service_name} service")
        else:
            print(f"Warning: Template directory for {service_name} does not exist")

def update_app_files(source_root, target_root):
    """Update the app.py and config.py for each service"""
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
        
        # Note: We don't copy app.py as each service has its own specialized app.py
        # Instead, we could update app.py files if needed

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
    
    print("\nSync completed successfully.")

if __name__ == "__main__":
    main()