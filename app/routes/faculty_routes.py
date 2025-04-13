<<<<<<< HEAD
from flask import Blueprint, render_template
from app.utils.auth_utils import login_required
from app.utils.auth_middleware import role_required

bp = Blueprint('faculty', __name__, url_prefix='/faculty')


@bp.route('/add_project')
@role_required("faculty")
=======
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import and_, func, or_

from app import db
from app.models.application import ApplicationForm
from app.models.faculty import Faculty
from app.models.intern import InternDetail
from app.models.milestone_submission import MilestoneSubmission
from app.models.project import Project
from app.models.research_proposal import ResearchProposal
from app.models.weekly_submission import WeeklySubmission
from app.utils.auth_utils import role_required

bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@bp.route('/')
@role_required('faculty')
def dashboard():
    """Faculty dashboard displaying an overview of projects and applications"""
    faculty_id = get_jwt_identity()
    faculty = Faculty.query.get_or_404(faculty_id)
    
    projects = Project.query.filter_by(faculty_id=faculty_id).all()
    project_count = len(projects)
    
    project_ids = [p.project_id for p in projects]
    
    pending_count = ApplicationForm.query.filter(
        ApplicationForm.project_code.in_(project_ids),
        ApplicationForm.status == 'pending'
    ).count()
    
    approved_count = ApplicationForm.query.filter(
        ApplicationForm.project_code.in_(project_ids),
        ApplicationForm.status == 'approved'
    ).count()
    
    rejected_count = ApplicationForm.query.filter(
        ApplicationForm.project_code.in_(project_ids),
        ApplicationForm.status == 'rejected'
    ).count()
    
    research_proposals = ResearchProposal.query.filter_by(faculty_id=faculty_id).all()
    pending_proposals = len([p for p in research_proposals if p.status == 'pending'])
    
    recent_weekly_submissions = WeeklySubmission.query.filter_by(
        faculty_id=faculty_id, 
        rating=None
    ).order_by(WeeklySubmission.submission_date.desc()).limit(5).all()
    
    recent_milestone_submissions = MilestoneSubmission.query.filter_by(
        faculty_id=faculty_id, 
        rating=None
    ).order_by(MilestoneSubmission.submission_date.desc()).limit(5).all()
    
    return render_template('faculty/dashboard.html',
                          faculty=faculty,
                          project_count=project_count,
                          pending_count=pending_count,
                          approved_count=approved_count,
                          rejected_count=rejected_count,
                          pending_proposals=pending_proposals,
                          recent_weekly_submissions=recent_weekly_submissions,
                          recent_milestone_submissions=recent_milestone_submissions)

@bp.route('/add_project', methods=['GET', 'POST'])
@role_required('faculty')
>>>>>>> dbc47f20582d9a7ed8a66662f89a68f595b06d3e
def add_project():
    """Add a new project"""
    if request.method == 'POST':
        faculty_id = get_jwt_identity()
        faculty = Faculty.query.get_or_404(faculty_id)
        
        project_title = request.form.get('project_title')
        project_description = request.form.get('project_description')
        number_of_student = request.form.get('number_of_student')
        faculty_email = request.form.get('faculty_email')
        
        new_project = Project(
            project_title=project_title,
            project_description=project_description,
            number_of_student=int(number_of_student),
            faculty_email=faculty_email,
            faculty_id=faculty_id,
            project_mode="remote"  # Default mode
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        flash('Project added successfully!', 'success')
        return redirect('/faculty/projects')
        
    return render_template('faculty/add_project.html')

@bp.route('/projects')
@role_required('faculty')
def projects():
    """View all projects created by the faculty"""
    faculty_id = get_jwt_identity()
    projects = Project.query.filter_by(faculty_id=faculty_id).all()
    
    project_data = []
    for project in projects:
        application_count = ApplicationForm.query.filter_by(project_code=project.project_id).count()
        pending_count = ApplicationForm.query.filter_by(
            project_code=project.project_id,
            status='pending'
        ).count()
        approved_count = ApplicationForm.query.filter_by(
            project_code=project.project_id,
            status='approved'
        ).count()
        
        project_data.append({
            'project': project,
            'application_count': application_count,
            'pending_count': pending_count,
            'approved_count': approved_count
        })
    
    return render_template('faculty/projects.html', project_data=project_data)

@bp.route('/project/<int:project_id>')
@role_required('faculty')
def view_project(project_id):
    """View details of a specific project"""
    faculty_id = get_jwt_identity()
    project = Project.query.filter_by(project_id=project_id, faculty_id=faculty_id).first_or_404()
    
    # Get all applications for this project
    applications = db.session.query(ApplicationForm, InternDetail).\
        join(InternDetail, InternDetail.intern_id == ApplicationForm.intern_id).\
        filter(ApplicationForm.project_code == project_id).all()
        
    return render_template('faculty/view_project.html', 
                          project=project, 
                          applications=applications)

@bp.route('/applications')
@role_required('faculty')
def applications():
    """View all applications for faculty's projects with filtering"""
    faculty_id = get_jwt_identity()
    status_filter = request.args.get('status', 'all')
    project_filter = request.args.get('project_id', 'all')
    
    # Get all projects by this faculty
    projects = Project.query.filter_by(faculty_id=faculty_id).all()
    project_ids = [p.project_id for p in projects]
    
    # Base query joining applications with intern details
    query = db.session.query(ApplicationForm, InternDetail, Project).\
        join(InternDetail, InternDetail.intern_id == ApplicationForm.intern_id).\
        join(Project, Project.project_id == ApplicationForm.project_code).\
        filter(ApplicationForm.project_code.in_(project_ids))
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter(ApplicationForm.status == status_filter)
    
    if project_filter != 'all':
        query = query.filter(ApplicationForm.project_code == int(project_filter))
    
    # Execute query
    applications = query.all()
    
    return render_template('faculty/applications.html',
                          applications=applications,
                          projects=projects,
                          status_filter=status_filter,
                          project_filter=project_filter)

@bp.route('/application/<int:application_id>', methods=['GET', 'POST'])
@role_required('faculty')
def application_detail(application_id):
    """View and process a specific application"""
    faculty_id = get_jwt_identity()
    
    # Get application with intern and project details
    application_data = db.session.query(ApplicationForm, InternDetail, Project).\
        join(InternDetail, InternDetail.intern_id == ApplicationForm.intern_id).\
        join(Project, Project.project_id == ApplicationForm.project_code).\
        filter(ApplicationForm.application_id == application_id).\
        filter(Project.faculty_id == faculty_id).first_or_404()
    
    application, intern, project = application_data
    
    if request.method == 'POST':
        action = request.form.get('action')
        feedback = request.form.get('feedback', '')
        
        if action == 'approve':
            application.status = 'approved'
            application.faculty_feedback = feedback
            
            # Optional: Mark intern as selected
            intern_obj = InternDetail.query.get(intern.intern_id)
            if intern_obj:
                intern_obj.isSelected = 1
                
        elif action == 'reject':
            application.status = 'rejected'
            application.faculty_feedback = feedback
        
        db.session.commit()
        flash('Application updated successfully', 'success')
        return redirect('/faculty/applications')
        
    return render_template('faculty/application_detail.html',
                          application=application,
                          intern=intern,
                          project=project)

@bp.route('/research_proposals')
@role_required('faculty')
def research_proposals():
    """View all research proposals with filtering"""
    faculty_id = get_jwt_identity()
    status_filter = request.args.get('status', 'all')
    project_filter = request.args.get('project_id', 'all')
    
    # Get all projects by this faculty
    projects = Project.query.filter_by(faculty_id=faculty_id).all()
    
    # Base query joining proposals with intern details and projects
    query = db.session.query(ResearchProposal, InternDetail, Project).\
        join(InternDetail, InternDetail.intern_id == ResearchProposal.intern_id).\
        join(Project, Project.project_id == ResearchProposal.project_id).\
        filter(ResearchProposal.faculty_id == faculty_id)
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter(ResearchProposal.status == status_filter)
    
    if project_filter != 'all':
        query = query.filter(ResearchProposal.project_id == int(project_filter))
    
    # Execute query
    proposals = query.all()
    
    return render_template('faculty/research_proposals.html',
                          proposals=proposals,
                          projects=projects,
                          status_filter=status_filter,
                          project_filter=project_filter)

@bp.route('/research_proposal/<int:proposal_id>', methods=['GET', 'POST'])
@role_required('faculty')
def research_proposal_detail(proposal_id):
    """View and process a specific research proposal"""
    faculty_id = get_jwt_identity()
    
    # Get proposal with intern and project details
    proposal_data = db.session.query(ResearchProposal, InternDetail, Project).\
        join(InternDetail, InternDetail.intern_id == ResearchProposal.intern_id).\
        join(Project, Project.project_id == ResearchProposal.project_id).\
        filter(ResearchProposal.proposal_id == proposal_id).\
        filter(ResearchProposal.faculty_id == faculty_id).first_or_404()
    
    proposal, intern, project = proposal_data
    
    if request.method == 'POST':
        action = request.form.get('action')
        feedback = request.form.get('feedback', '')
        
        if action in ['approve', 'reject']:
            proposal.status = 'approved' if action == 'approve' else 'rejected'
            proposal.feedback = feedback
            proposal.feedback_date = datetime.now()
            
            db.session.commit()
            flash('Research proposal updated successfully', 'success')
            return redirect('/faculty/research_proposals')
        
    return render_template('faculty/research_proposal_detail.html',
                          proposal=proposal,
                          intern=intern,
                          project=project)

@bp.route('/weekly_submissions')
@role_required('faculty')
def weekly_submissions():
    """View all weekly submissions with filtering"""
    faculty_id = get_jwt_identity()
    status_filter = request.args.get('status', 'all')  # rated, unrated
    type_filter = request.args.get('type', 'all')  # tuesday, friday
    project_filter = request.args.get('project_id', 'all')
    
    # Get all projects by this faculty
    projects = Project.query.filter_by(faculty_id=faculty_id).all()
    
    # Base query joining submissions with intern details and projects
    query = db.session.query(WeeklySubmission, InternDetail, Project).\
        join(InternDetail, InternDetail.intern_id == WeeklySubmission.intern_id).\
        join(Project, Project.project_id == WeeklySubmission.project_id).\
        filter(WeeklySubmission.faculty_id == faculty_id)
    
    # Apply filters
    if status_filter == 'rated':
        query = query.filter(WeeklySubmission.rating != None)
    elif status_filter == 'unrated':
        query = query.filter(WeeklySubmission.rating == None)
    
    if type_filter != 'all':
        query = query.filter(WeeklySubmission.submission_type == type_filter)
    
    if project_filter != 'all':
        query = query.filter(WeeklySubmission.project_id == int(project_filter))
    
    # Sort by submission date, newest first
    query = query.order_by(WeeklySubmission.submission_date.desc())
    
    # Execute query
    submissions = query.all()
    
    return render_template('faculty/weekly_submissions.html',
                          submissions=submissions,
                          projects=projects,
                          status_filter=status_filter,
                          type_filter=type_filter,
                          project_filter=project_filter)

@bp.route('/weekly_submission/<int:submission_id>', methods=['GET', 'POST'])
@role_required('faculty')
def weekly_submission_detail(submission_id):
    """View and rate a specific weekly submission"""
    faculty_id = get_jwt_identity()
    
    # Get submission with intern and project details
    submission_data = db.session.query(WeeklySubmission, InternDetail, Project).\
        join(InternDetail, InternDetail.intern_id == WeeklySubmission.intern_id).\
        join(Project, Project.project_id == WeeklySubmission.project_id).\
        filter(WeeklySubmission.submission_id == submission_id).\
        filter(WeeklySubmission.faculty_id == faculty_id).first_or_404()
    
    submission, intern, project = submission_data
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        feedback = request.form.get('feedback', '')
        
        if rating:
            submission.rating = int(rating)
            submission.feedback = feedback
            submission.feedback_date = datetime.now()
            
            db.session.commit()
            flash('Submission rated successfully', 'success')
            return redirect('/faculty/weekly_submissions')
        
    return render_template('faculty/weekly_submission_detail.html',
                          submission=submission,
                          intern=intern,
                          project=project)

@bp.route('/milestone_submissions')
@role_required('faculty')
def milestone_submissions():
    """View all milestone submissions with filtering"""
    faculty_id = get_jwt_identity()
    status_filter = request.args.get('status', 'all')  # rated, unrated
    type_filter = request.args.get('type', 'all')  # midterm, pre_final
    project_filter = request.args.get('project_id', 'all')
    
    # Get all projects by this faculty
    projects = Project.query.filter_by(faculty_id=faculty_id).all()
    
    # Base query joining submissions with intern details and projects
    query = db.session.query(MilestoneSubmission, InternDetail, Project).\
        join(InternDetail, InternDetail.intern_id == MilestoneSubmission.intern_id).\
        join(Project, Project.project_id == MilestoneSubmission.project_id).\
        filter(MilestoneSubmission.faculty_id == faculty_id)
    
    # Apply filters
    if status_filter == 'rated':
        query = query.filter(MilestoneSubmission.rating != None)
    elif status_filter == 'unrated':
        query = query.filter(MilestoneSubmission.rating == None)
    
    if type_filter != 'all':
        query = query.filter(MilestoneSubmission.submission_type == type_filter)
    
    if project_filter != 'all':
        query = query.filter(MilestoneSubmission.project_id == int(project_filter))
    
    # Sort by submission date, newest first
    query = query.order_by(MilestoneSubmission.submission_date.desc())
    
    # Execute query
    submissions = query.all()
    
    return render_template('faculty/milestone_submissions.html',
                          submissions=submissions,
                          projects=projects,
                          status_filter=status_filter,
                          type_filter=type_filter,
                          project_filter=project_filter)

@bp.route('/milestone_submission/<int:submission_id>', methods=['GET', 'POST'])
@role_required('faculty')
def milestone_submission_detail(submission_id):
    """View and rate a specific milestone submission"""
    faculty_id = get_jwt_identity()
    
    # Get submission with intern and project details
    submission_data = db.session.query(MilestoneSubmission, InternDetail, Project).\
        join(InternDetail, InternDetail.intern_id == MilestoneSubmission.intern_id).\
        join(Project, Project.project_id == MilestoneSubmission.project_id).\
        filter(MilestoneSubmission.submission_id == submission_id).\
        filter(MilestoneSubmission.faculty_id == faculty_id).first_or_404()
    
    submission, intern, project = submission_data
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        remarks = request.form.get('remarks', '')
        
        if rating:
            submission.rating = int(rating)
            submission.remarks = remarks
            submission.review_date = datetime.now()
            
            db.session.commit()
            flash('Milestone submission rated successfully', 'success')
            return redirect('/faculty/milestone_submissions')
        
    return render_template('faculty/milestone_submission_detail.html',
                          submission=submission,
                          intern=intern,
                          project=project)

@bp.route('/profile')
@role_required('faculty')
def profile():
    """View faculty profile"""
    faculty_id = get_jwt_identity()
    faculty = Faculty.query.get_or_404(faculty_id)
    
    return render_template('faculty/profile.html', faculty=faculty)