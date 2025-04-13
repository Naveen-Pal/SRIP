from datetime import datetime, timedelta
import os

from flask import Blueprint, flash, redirect, render_template, request
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from app import db
from app.models.application import ApplicationForm
from app.models.faculty import Faculty
from app.models.intern import InternDetail
from app.models.milestone_submission import MilestoneSubmission
from app.models.project import Project
from app.models.research_proposal import ResearchProposal
from app.models.weekly_submission import WeeklySubmission
from app.utils.auth_utils import role_required

bp = Blueprint('selected_intern', __name__, url_prefix='/selected_intern')

<<<<<<< HEAD
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity,get_jwt
from app.utils.auth_middleware import role_required
@jwt_required()  # Extracts JWT from cookie
@bp.route('/home', methods=['GET'])
@role_required("selected_intern")
=======
@bp.route('/')
@role_required('selected_intern')
def dashboard():
    intern_id = get_jwt_identity()
    intern = InternDetail.query.get_or_404(intern_id)
    
    # Get application and project details
    application = ApplicationForm.query.filter_by(intern_id=str(intern_id), status='approved').first()
    
    if not application:
        return render_template('intern/not_selected.html')
    
    project_id = application.project_code
    project = Project.query.get_or_404(project_id)
    faculty = Faculty.query.get_or_404(project.faculty_id)
    
    # Research proposal status
    proposal = ResearchProposal.query.filter_by(
        intern_id=intern_id, 
        project_id=project_id
    ).first()
    
    # Recent weekly submissions
    weekly_submissions = WeeklySubmission.query.filter_by(
        intern_id=intern_id, 
        project_id=project_id
    ).order_by(WeeklySubmission.submission_date.desc()).limit(5).all()
    
    # Milestone submissions
    milestone_submissions = MilestoneSubmission.query.filter_by(
        intern_id=intern_id, 
        project_id=project_id
    ).all()
    
    return render_template('intern/dashboard.html',
                          intern=intern,
                          project=project,
                          faculty=faculty,
                          proposal=proposal,
                          weekly_submissions=weekly_submissions,
                          milestone_submissions=milestone_submissions)

@bp.route('/home')
@role_required('selected_intern')
>>>>>>> dbc47f20582d9a7ed8a66662f89a68f595b06d3e
def home():
    return redirect('/selected_intern/')

@bp.route('/research_proposal', methods=['GET', 'POST'])
@role_required('selected_intern')
def research_proposal():
    intern_id = get_jwt_identity()
    intern = InternDetail.query.get_or_404(intern_id)
    
    # Get application and project details
    application = ApplicationForm.query.filter_by(intern_id=str(intern_id), status='approved').first()
    
    if not application:
        return redirect('/selected_intern')
    
    project_id = application.project_code
    project = Project.query.get_or_404(project_id)
    faculty = Faculty.query.get_or_404(project.faculty_id)
    
    # Check if proposal already exists
    existing_proposal = ResearchProposal.query.filter_by(
        intern_id=intern_id, 
        project_id=project_id
    ).first()
    
    if request.method == 'POST' and not existing_proposal:
        title = request.form.get('title')
        proposal_content = request.form.get('proposal_content')
        
        if not title or not proposal_content:
            flash('All fields are required', 'danger')
            return redirect('/selected_intern/research_proposal')
            
        new_proposal = ResearchProposal(
            intern_id=intern_id,
            project_id=project_id,
            faculty_id=faculty.faculty_id,
            title=title,
            proposal_content=proposal_content,
            status='pending'
        )
        
        db.session.add(new_proposal)
        db.session.commit()
        
        flash('Research proposal submitted successfully!', 'success')
        return redirect('/selected_intern/research_proposal')
    
    return render_template('intern/research_proposal.html',
                          intern=intern,
                          project=project,
                          faculty=faculty,
                          proposal=existing_proposal)

@bp.route('/weekly_submissions')
@role_required('selected_intern')
def weekly_submissions_list():
    intern_id = get_jwt_identity()
    intern = InternDetail.query.get_or_404(intern_id)
    
    # Get application and project details
    application = ApplicationForm.query.filter_by(intern_id=str(intern_id), status='approved').first()
    
    if not application:
        return redirect('/selected_intern')
    
    project_id = application.project_code
    project = Project.query.get_or_404(project_id)
    
    # Get all weekly submissions
    submissions = WeeklySubmission.query.filter_by(
        intern_id=intern_id, 
        project_id=project_id
    ).order_by(WeeklySubmission.submission_date.desc()).all()
    
    return render_template('intern/weekly_submissions.html',
                          intern=intern,
                          project=project,
                          submissions=submissions)

@bp.route('/weekly_submission/<submission_type>', methods=['GET', 'POST'])
@role_required('selected_intern')
def weekly_submission(submission_type):
    if submission_type not in ['tuesday', 'friday']:
        flash('Invalid submission type', 'danger')
        return redirect('/selected_intern/weekly_submissions')
    
    intern_id = get_jwt_identity()
    intern = InternDetail.query.get_or_404(intern_id)
    
    # Get application and project details
    application = ApplicationForm.query.filter_by(intern_id=str(intern_id), status='approved').first()
    
    if not application:
        return redirect('/selected_intern')
    
    project_id = application.project_code
    project = Project.query.get_or_404(project_id)
    faculty = Faculty.query.get_or_404(project.faculty_id)
    
    # Check if already submitted for current week
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    
    existing_submission = WeeklySubmission.query.filter_by(
        intern_id=intern_id,
        project_id=project_id,
        submission_type=submission_type
    ).filter(
        WeeklySubmission.submission_date >= start_of_week
    ).first()
    
    if request.method == 'POST' and not existing_submission:
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('All fields are required', 'danger')
            return redirect(f'/selected_intern/weekly_submission/{submission_type}')
            
        new_submission = WeeklySubmission(
            intern_id=intern_id,
            project_id=project_id,
            faculty_id=faculty.faculty_id,
            title=title,
            content=content,
            submission_type=submission_type
        )
        
        db.session.add(new_submission)
        db.session.commit()
        
        flash('Weekly submission completed successfully!', 'success')
        return redirect('/selected_intern/weekly_submissions')
    
    return render_template('intern/weekly_submission_form.html',
                          intern=intern,
                          project=project,
                          submission_type=submission_type,
                          existing_submission=existing_submission)

@bp.route('/milestone_submissions')
@role_required('selected_intern')
def milestone_submissions_list():
    intern_id = get_jwt_identity()
    intern = InternDetail.query.get_or_404(intern_id)
    
    # Get application and project details
    application = ApplicationForm.query.filter_by(intern_id=str(intern_id), status='approved').first()
    
    if not application:
        return redirect('/selected_intern')
    
    project_id = application.project_code
    project = Project.query.get_or_404(project_id)
    
    # Get all milestone submissions
    submissions = MilestoneSubmission.query.filter_by(
        intern_id=intern_id, 
        project_id=project_id
    ).order_by(MilestoneSubmission.submission_date.desc()).all()
    
    return render_template('intern/milestone_submissions.html',
                          intern=intern,
                          project=project,
                          submissions=submissions)

@bp.route('/milestone_submission/<submission_type>', methods=['GET', 'POST'])
@role_required('selected_intern')
def milestone_submission(submission_type):
    if submission_type not in ['midterm', 'pre_final']:
        flash('Invalid submission type', 'danger')
        return redirect('/selected_intern/milestone_submissions')
    
    intern_id = get_jwt_identity()
    intern = InternDetail.query.get_or_404(intern_id)
    
    # Get application and project details
    application = ApplicationForm.query.filter_by(intern_id=str(intern_id), status='approved').first()
    
    if not application:
        return redirect('/selected_intern')
    
    project_id = application.project_code
    project = Project.query.get_or_404(project_id)
    faculty = Faculty.query.get_or_404(project.faculty_id)
    
    # Check if already submitted
    existing_submission = MilestoneSubmission.query.filter_by(
        intern_id=intern_id,
        project_id=project_id,
        submission_type=submission_type
    ).first()
    
    if request.method == 'POST' and not existing_submission:
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('All fields are required', 'danger')
            return redirect(f'/selected_intern/milestone_submission/{submission_type}')
        
        # Handle document upload
        document_path = None
        if 'document' in request.files:
            document = request.files['document']
            if document.filename:
                filename = secure_filename(f"{intern_id}_{submission_type}_{document.filename}")
                upload_path = os.path.join('app/static/uploads', filename)
                document.save(upload_path)
                document_path = f"/static/uploads/{filename}"
            
        new_submission = MilestoneSubmission(
            intern_id=intern_id,
            project_id=project_id,
            faculty_id=faculty.faculty_id,
            title=title,
            content=content,
            submission_type=submission_type,
            document_path=document_path
        )
        
        db.session.add(new_submission)
        db.session.commit()
        
        flash('Milestone submission completed successfully!', 'success')
        return redirect('/selected_intern/milestone_submissions')
    
    return render_template('intern/milestone_submission_form.html',
                          intern=intern,
                          project=project,
                          submission_type=submission_type,
                          existing_submission=existing_submission)

@bp.route('/profile')
@role_required('selected_intern')
def profile():
    intern_id = get_jwt_identity()
    intern = InternDetail.query.get_or_404(intern_id)
    
    return render_template('intern/profile.html', intern=intern)
