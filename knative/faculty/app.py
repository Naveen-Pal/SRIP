from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from config import Config
from database import db

jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Import routes here to avoid circular imports
    from faculty_routes import bp
    
    # Register blueprints
    app.register_blueprint(bp)
    
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
