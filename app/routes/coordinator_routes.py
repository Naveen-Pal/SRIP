from flask import Blueprint, render_template, request, redirect
from app.utils.auth_utils import role_required
from app.models.faculty import Faculty
from app.models.project import Project
from app.models.application import ApplicationForm
from app.models.intern import InternDetail
from app.utils.email_utils import send_email
from app import db
from sqlalchemy import or_, and_, func

bp = Blueprint('coordinator', __name__, url_prefix='/coordinator')

@bp.route('/')
@role_required('coordinator')
def dashboard():
    """Main coordinator dashboard"""
    faculty_count = Faculty.query.count()
    project_count = Project.query.count()
    intern_count = InternDetail.query.count()
    application_count = ApplicationForm.query.count()
    selected_count = InternDetail.query.filter_by(isSelected=1).count()
    pending_count = InternDetail.query.filter_by(isSelected=0).count()
    
    return render_template('coordinator/dashboard.html', 
                          faculty_count=faculty_count,
                          project_count=project_count,
                          intern_count=intern_count,
                          application_count=application_count,
                          selected_count=selected_count,
                          pending_count=pending_count)

@bp.route('/faculty_list', methods=['GET', 'POST'])
@role_required('coordinator')
def faculty_list():
    """List all faculty with their projects and applicants"""
    # Handle POST requests for faculty approval/deletion
    if request.method == 'POST':
        print("hello")
        try:
            action = request.form.get('action')
            faculty_id = request.form.get('faculty_id')
            faculty = Faculty.query.get(faculty_id)
            
            if not faculty:
                return "Faculty not found", 404
            
            if action == 'toggle':
                faculty.allowed = 1 if faculty.allowed == 0 else 0
                db.session.commit()
            elif action == 'delete':
                db.session.delete(faculty)
                db.session.commit()
            return redirect('/coordinator/faculty_list')
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    
    # Handle GET requests for faculty listing
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'faculty_id')
    order = request.args.get('order', 'asc')
    filter_type = request.args.get('filter', 'all')
    
    query = Faculty.query
    
    # Apply filter if provided
    if filter_type == 'allowed':
        query = query.filter_by(allowed=1)
    elif filter_type == 'unallowed':
        query = query.filter_by(allowed=0)
    
    # Apply search filter if provided
    if search:
        query = query.filter(or_(
            Faculty.full_name.ilike(f'%{search}%'),
            Faculty.email.ilike(f'%{search}%')
        ))
    
    # Apply sorting
    if order == 'asc':
        query = query.order_by(getattr(Faculty, sort_by).asc())
    else:
        query = query.order_by(getattr(Faculty, sort_by).desc())
    
    faculties = query.all()
    
    # Get project counts for each faculty
    faculty_data = []
    for faculty in faculties:
        projects = Project.query.filter_by(faculty_id=faculty.faculty_id).all()
        project_count = len(projects)
        
        # Count applications for this faculty's projects
        application_count = 0
        for project in projects:
            applications = ApplicationForm.query.filter_by(project_code=project.project_id).count()
            application_count += applications
            
        faculty_data.append({
            'faculty': faculty,
            'project_count': project_count,
            'application_count': application_count
        })
        
    return render_template('coordinator/faculty_list.html', 
                          faculty_data=faculty_data, 
                          search=search,
                          sort_by=sort_by,
                          order=order,
                          filter_type=filter_type)

@bp.route('/faculty/<int:faculty_id>/projects')
@role_required('coordinator')
def faculty_projects(faculty_id):
    """Show all projects for a specific faculty"""
    faculty = Faculty.query.get_or_404(faculty_id)
    projects = Project.query.filter_by(faculty_id=faculty_id).all()
    
    # Get applicant counts for each project
    project_data = []
    for project in projects:
        application_count = ApplicationForm.query.filter_by(project_code=project.project_id).count()
        selected_count = InternDetail.query.join(
            ApplicationForm, 
            ApplicationForm.intern_id == InternDetail.intern_id
        ).filter(
            ApplicationForm.project_code == project.project_id,
            InternDetail.isSelected == 1
        ).count()
        
        project_data.append({
            'project': project,
            'application_count': application_count,
            'selected_count': selected_count
        })
        
    return render_template('coordinator/faculty_projects.html', 
                          faculty=faculty,
                          project_data=project_data)

@bp.route('/interns')
@role_required('coordinator')
def interns_list():
    """List all interns with filtering options"""
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    faculty_id = request.args.get('faculty_id', 'all')
    project_id = request.args.get('project_id', 'all')
    sort_by = request.args.get('sort', 'intern_id')
    order = request.args.get('order', 'asc')
    
    # Start with base join query
    query = db.session.query(InternDetail, ApplicationForm, Project, Faculty).\
            join(ApplicationForm, ApplicationForm.intern_id == InternDetail.intern_id).\
            join(Project, Project.project_id == ApplicationForm.project_code).\
            join(Faculty, Faculty.faculty_id == Project.faculty_id)
    
    # Apply filters
    if search:
        query = query.filter(or_(
            InternDetail.full_name.ilike(f'%{search}%'),
            InternDetail.email.ilike(f'%{search}%'),
            InternDetail.college_name.ilike(f'%{search}%')
        ))
        
    if status != 'all':
        is_selected = 1 if status == 'selected' else 0
        query = query.filter(InternDetail.isSelected == is_selected)
        
    if faculty_id != 'all':
        query = query.filter(Faculty.faculty_id == int(faculty_id))
        
    if project_id != 'all':
        query = query.filter(Project.project_id == int(project_id))
        
    # Apply sorting
    if sort_by in ['full_name', 'email', 'college_name', 'isSelected']:
        if order == 'asc':
            query = query.order_by(getattr(InternDetail, sort_by).asc())
        else:
            query = query.order_by(getattr(InternDetail, sort_by).desc())
    elif sort_by == 'faculty_name':
        if order == 'asc':
            query = query.order_by(Faculty.full_name.asc())
        else:
            query = query.order_by(Faculty.full_name.desc())
    elif sort_by == 'project_title':
        if order == 'asc':
            query = query.order_by(Project.project_title.asc())
        else:
            query = query.order_by(Project.project_title.desc())
    else:
        if order == 'asc':
            query = query.order_by(InternDetail.intern_id.asc())
        else:
            query = query.order_by(InternDetail.intern_id.desc())
    
    # Execute query
    results = query.all()
    
    # Prepare data for template
    interns_data = []
    for intern, application, project, faculty in results:
        interns_data.append({
            'intern': intern,
            'application': application,
            'project': project,
            'faculty': faculty
        })
    
    # Get all faculties and projects for filters
    faculties = Faculty.query.all()
    projects = Project.query.all()
    
    return render_template('coordinator/interns_list.html',
                          interns_data=interns_data,
                          faculties=faculties,
                          projects=projects,
                          search=search,
                          status=status,
                          faculty_id=faculty_id,
                          project_id=project_id,
                          sort_by=sort_by,
                          order=order)

@bp.route('/applications')
@role_required('coordinator')
def applications_list():
    """List all applications with filtering options"""
    search = request.args.get('search', '')
    faculty_id = request.args.get('faculty_id', 'all')
    project_id = request.args.get('project_id', 'all')
    sort_by = request.args.get('sort', 'application_id')
    order = request.args.get('order', 'asc')
    
    # Start with base join query
    query = db.session.query(ApplicationForm, InternDetail, Project, Faculty).\
            join(InternDetail, InternDetail.intern_id == ApplicationForm.intern_id).\
            join(Project, Project.project_id == ApplicationForm.project_code).\
            join(Faculty, Faculty.faculty_id == Project.faculty_id)
    
    # Apply filters
    if search:
        query = query.filter(or_(
            InternDetail.full_name.ilike(f'%{search}%'),
            InternDetail.email.ilike(f'%{search}%')
        ))
        
    if faculty_id != 'all':
        query = query.filter(Faculty.faculty_id == int(faculty_id))
        
    if project_id != 'all':
        query = query.filter(Project.project_id == int(project_id))
        
    # Apply sorting
    if sort_by == 'full_name':
        if order == 'asc':
            query = query.order_by(InternDetail.full_name.asc())
        else:
            query = query.order_by(InternDetail.full_name.desc())
    elif sort_by == 'faculty_name':
        if order == 'asc':
            query = query.order_by(Faculty.full_name.asc())
        else:
            query = query.order_by(Faculty.full_name.desc())
    elif sort_by == 'project_title':
        if order == 'asc':
            query = query.order_by(Project.project_title.asc())
        else:
            query = query.order_by(Project.project_title.desc())
    else:
        if order == 'asc':
            query = query.order_by(ApplicationForm.application_id.asc())
        else:
            query = query.order_by(ApplicationForm.application_id.desc())
    
    # Execute query
    results = query.all()
    
    # Prepare data for template
    applications_data = []
    for application, intern, project, faculty in results:
        applications_data.append({
            'application': application,
            'intern': intern,
            'project': project,
            'faculty': faculty
        })
    
    # Get all faculties and projects for filters
    faculties = Faculty.query.all()
    projects = Project.query.all()
    
    return render_template('coordinator/applications_list.html',
                          applications_data=applications_data,
                          faculties=faculties,
                          projects=projects,
                          search=search,
                          faculty_id=faculty_id,
                          project_id=project_id,
                          sort_by=sort_by,
                          order=order)

@bp.route('/toggle_selection/<int:intern_id>', methods=['POST'])
@role_required('coordinator')
def toggle_selection(intern_id):
    """Toggle the selection status of an intern"""
    intern = InternDetail.query.get_or_404(intern_id)
    intern.isSelected = 0 if intern.isSelected == 1 else 1
    db.session.commit()
    
    return redirect(request.referrer)

@bp.route('/email_selected_interns', methods=['GET', 'POST'])
@role_required('coordinator')
def email_selected_interns():
    """Email selected interns"""
    if request.method == 'POST':
        subject = request.form.get('subject')
        text_body = request.form.get('text_body')
        html_body = request.form.get('html_body')
        
        # Get all selected interns
        selected_interns = InternDetail.query.filter_by(isSelected=1).all()
        recipients = [intern.email for intern in selected_interns]
        
        try:
            # Send email to all selected interns
            for recipient in recipients:
                send_email(subject, sender='srip@yourdomain.com', recipients=[recipient], 
                           text_body=text_body, html_body=html_body)
            
            return render_template('coordinator/email_sent.html', 
                                  recipient_type="selected interns",
                                  count=len(recipients))
        except Exception as e:
            return render_template('coordinator/email_error.html', error=str(e))
    
    return render_template('coordinator/email_selected_interns.html', recipient_type="Selected Interns")

@bp.route('/email_waitlisted_interns', methods=['GET', 'POST'])
@role_required('coordinator')
def email_waitlisted_interns():
    """Email waitlisted interns"""
    if request.method == 'POST':
        subject = request.form.get('subject')
        text_body = request.form.get('text_body')
        html_body = request.form.get('html_body')
        
        # Get all waitlisted interns
        waitlisted_interns = InternDetail.query.filter_by(isSelected=0).all()
        recipients = [intern.email for intern in waitlisted_interns]
        
        try:
            # Send email to all waitlisted interns
            for recipient in recipients:
                send_email(subject, sender='srip@yourdomain.com', recipients=[recipient], 
                           text_body=text_body, html_body=html_body)
            
            return render_template('coordinator/email_sent.html', 
                                  recipient_type="waitlisted interns",
                                  count=len(recipients))
        except Exception as e:
            return render_template('coordinator/email_error.html', error=str(e))
    
    return render_template('coordinator/email_selected_interns.html', recipient_type="Waitlisted Interns")

@bp.route('/confirm_participation/<int:intern_id>', methods=['POST'])
@role_required('coordinator')
def confirm_participation(intern_id):
    """Manually confirm an intern's participation"""
    intern = InternDetail.query.get_or_404(intern_id)
    intern.confirmed = True
    db.session.commit()
    
    return redirect(request.referrer)

@bp.route('/email_faculty')
@role_required('coordinator')
def email_faculty():
    """Email selected interns"""
    return render_template('coordinator/email_selected_interns.html', recipient_type="Faculty")

@bp.route('/add_faculty', methods=['GET', 'POST'])
@role_required('coordinator')
def add_faculty():
    """Add a new faculty member"""
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        discipline = request.form.get('discipline', '')
        
        # Check if faculty with this email already exists
        existing_faculty = Faculty.query.filter_by(email=email).first()
        if existing_faculty:
            return render_template('coordinator/add_faculty.html', 
                                  error="A faculty with this email already exists")
        
        # Create new faculty with a default password
        new_faculty = Faculty(
            email=email,
            full_name=full_name,
            password="changeme",  # Should be hashed in a real application
            allowed=1  # Auto-approve when added by coordinator
        )
        
        db.session.add(new_faculty)
        db.session.commit()
        
        return redirect('/coordinator/faculty_list')
    
    return render_template('coordinator/add_faculty.html')