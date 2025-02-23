from app.models.session import Session

def verify_session(session_id, user_type):
    session = Session.query.filter_by(session_id=session_id, user_type=user_type, is_active=True).first()
    return session is not None