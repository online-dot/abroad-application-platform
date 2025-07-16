# app/routes/admin_routes.py

from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    session, request, Response
)
from flask_login import login_required, current_user
from app.models.user import User
from app.models.application import Application
from app.models import db
# Add this import at the top of admin_routes.py
from utils.email_utils import send_acceptance_email
from datetime import datetime

import csv
from io import StringIO

admin_bp = Blueprint('admin_bp', __name__)


def is_admin():
    """
    Check if the current logged-in user (from session) is an admin.
    Used to restrict access to admin-only routes.
    """
    user_id = session.get('user_id')
    if not user_id:
        return False

    user = User.query.get(user_id)
    return user and user.is_admin


@admin_bp.route('/admin/dashboard')
@login_required  # ✅ Requires login
def admin_dashboard():
    """
    Admin dashboard route.
    Only accessible to users with is_admin=True.
    """
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    return render_template('admin/dashboard.html', user=current_user)



@admin_bp.route('/admin/applications')
@login_required
def view_all_applications():
    """
    View all applications with filters, sorting, and pagination.
    Accessible to admin users only.
    """

    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    # --- Filter Parameters from Query ---
    email = request.args.get('email')
    submitted = request.args.get('submitted')
    approved = request.args.get('approved')
    passport_status = request.args.get('passport_status')

    # --- Pagination Parameters ---
    page = request.args.get('page', 1, type=int)
    per_page = 10  # You can change this to show more/less per page

    # --- Sorting Parameters ---
    sort_by = request.args.get('sort_by', 'id')  # Default: sort by ID
    sort_dir = request.args.get('sort_dir', 'asc')  # Default: ascending order

    # --- Begin Query ---
    query = Application.query.join(User)

    # Apply filters if provided
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if passport_status:
        query = query.filter(Application.passport_status == passport_status)
    if submitted == 'yes':
        query = query.filter(Application.submitted.is_(True))
    elif submitted == 'no':
        query = query.filter(Application.submitted.is_(False))
    if approved == 'yes':
        query = query.filter(Application.approved.is_(True))
    elif approved == 'no':
        query = query.filter(Application.approved.is_(False))

    # --- Allowed Sorting Columns (Prevent SQL injection) ---
    allowed_sort_columns = {
        'id': Application.id,
        'name': User.full_name,
        'email': User.email,
        'passport_status': Application.passport_status,
        'submitted': Application.submitted,
        'approved': Application.approved,
    }

    # Fallback to Application.id if sort_by is invalid
    sort_column = allowed_sort_columns.get(sort_by, Application.id)

    # Apply ascending or descending order
    sort_column = sort_column.desc() if sort_dir == 'desc' else sort_column.asc()

    # Add sorting to query
    query = query.order_by(sort_column)

    # --- Apply Pagination ---
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    applications = pagination.items  # Get only current page's applications

    # --- Render Template with Required Data ---
    return render_template(
        'admin/view_all_applications.html',
        applications=applications,
        pagination=pagination,      # ✅ Needed for pagination controls
        sort_by=sort_by,            # ✅ For sorting arrows in template
        sort_dir=sort_dir           # ✅ For toggling asc/desc
    )


@admin_bp.route('/admin/application/<int:app_id>/approve')
@login_required
def approve_application(app_id):
    """Approves application and sends acceptance email"""
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('auth.dashboard'))

    application = Application.query.get_or_404(app_id)
    
    if not application.approved:
        application.approved = True
        application.approved_at = datetime.utcnow()
        db.session.commit()

    # Always send acceptance email, even if already approved
    registration_number = f"2025{application.id:06d}"
    success, message = send_acceptance_email(
        to_email=application.user.email,
        user_name=application.user.full_name,
        registration_number=registration_number
    )

    if success:
        flash("✅ Application approved and acceptance email sent", "success")
    else:
        flash(f"⚠️ Approved but email failed: {message}", "warning")

    return redirect(url_for('admin_bp.view_application', app_id=app_id))

@admin_bp.route('/admin/application/<int:app_id>/send-acceptance')
@login_required
def send_acceptance_letter(app_id):
    """Manually resends acceptance email"""
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('auth.dashboard'))

    application = Application.query.get_or_404(app_id)
    registration_number = f"2025{application.id:06d}"
    
    success, message = send_acceptance_email(
        to_email=application.user.email,
        user_name=application.user.full_name,
        registration_number=registration_number
    )

    if success:
        flash("✅ Acceptance letter sent", "success")
    else:
        flash(f"❌ Failed to send: {message}", "danger")

    return redirect(url_for('admin_bp.view_application', app_id=app_id))

@admin_bp.route('/admin/application/<int:app_id>/send-reminder')
@login_required
def send_reminder_letter(app_id):
    """Manually sends reminder email"""
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('auth.dashboard'))

    application = Application.query.get_or_404(app_id)
    registration_number = f"2025{application.id:06d}"
    
    success, message = send_acceptance_email(
        to_email=application.user.email,
        user_name=application.user.full_name,
        registration_number=registration_number,
        is_reminder=True
    )

    if success:
        application.last_reminder_sent = datetime.utcnow()
        db.session.commit()
        flash("✅ Reminder sent", "success")
    else:
        flash(f"❌ Failed to send: {message}", "danger")

    return redirect(url_for('admin_bp.view_application', app_id=app_id))
@admin_bp.route('/admin/application/<int:app_id>/preview-email', methods=['GET'])
@login_required
def preview_acceptance_email(app_id):
    """
    Preview the acceptance email that would be sent
    """
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    application = Application.query.get_or_404(app_id)
    registration_number = f"2025{application.id:06d}"
    
    # Render the email template directly
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
            .notification {{ font-size: 16px; margin-bottom: 30px; }}
            .footer {{ margin-top: 30px; font-size: 14px; border-top: 1px solid #eee; padding-top: 15px; }}
            .signature {{ margin-top: 20px; }}
            .cta-button {{ 
                display: inline-block; 
                background-color: #0056b3; 
                color: white; 
                padding: 10px 20px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">CVE NOTIFICATION DEPARTMENT</div>
        <div class="notification">
            <h2>Acceptance Letter</h2>
            <p>NOTIFICATION</p>
            
            <p>Applicant {application.user.full_name}, Registration # {registration_number}, has been approved for Permanent Residency evaluation to Canada.</p>
            
            <p>This enables an immigration review for Permanent Residency status in Canada. Complete the online application to check if you meet the criteria for Employment based Express Entry to Canada.</p>
            
            <a href="https://www.yourwebsite.com/continue-application" class="cta-button">Complete your electronic application here</a>
            
            <p>➔ Your request for immigration services is confirmed</p>
            
            <p><strong>Late submissions will not be enrolled in 2025!</strong></p>
            
            <p>{application.user.full_name.split()[0]} - continue to your online application here.</p>
        </div>
        
        <div class="footer">
            <p>CVE will process and relay your application to authorized Canadian immigration consultants who will provide an assessment to apply. Canada will welcome another 395,000 new immigrants in 2025, many through the Express Entry immigration program for working families. An eligibility review is the first step in the application process. CVE provides services in multiple languages.</p>
            
            <div class="signature">
                <p>Secretary of Registry</p>
                <p>Canadian Visa Expert</p>
                <p><a href="https://www.canadianvisaexpert.com/">https://www.canadianvisaexpert.com/</a></p>
            </div>
        </div>
    </body>
    </html>
    """



@admin_bp.route('/admin/application/<int:app_id>/reject')
@login_required
def reject_application(app_id):
    """
    Mark an application as rejected (admin only).
    Sets 'approved' to False and clears approval timestamp.
    """
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    application = Application.query.get_or_404(app_id)
    application.approved = False
    application.approved_at = None
    db.session.commit()

    flash("❌ Application rejected/unapproved.", "info")
    return redirect(url_for('admin_bp.view_application', app_id=app_id))


@admin_bp.route('/admin/application/<int:app_id>')
@login_required
def view_application(app_id):
    """
    View full details of a single application.
    Admin access only.
    """
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    application = Application.query.get_or_404(app_id)
    user = application.user  # Related user object

    return render_template('admin/view_application_detail.html', application=application, user=user)


@admin_bp.route('/admin/applications/export')
@login_required
def export_applications_csv():
    """
    Export applications as CSV with applied filters.
    Only accessible to admins.
    """
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    # Same filters as list view
    email = request.args.get('email')
    submitted = request.args.get('submitted')
    approved = request.args.get('approved')
    passport_status = request.args.get('passport_status')

    query = Application.query.join(User)

    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if passport_status:
        query = query.filter(Application.passport_status == passport_status)
    if submitted == 'yes':
        query = query.filter(Application.submitted.is_(True))
    elif submitted == 'no':
        query = query.filter(Application.submitted.is_(False))
    if approved == 'yes':
        query = query.filter(Application.approved.is_(True))
    elif approved == 'no':
        query = query.filter(Application.approved.is_(False))

    applications = query.all()

    # Create CSV in-memory
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Applicant Name', 'Email', 'Passport Status', 'Submitted', 'Approved'])

    for app in applications:
        cw.writerow([
            app.user.full_name,
            app.user.email,
            app.passport_status.capitalize() if app.passport_status else '',
            'Yes' if app.submitted else 'No',
            'Yes' if app.approved else 'No',
        ])

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=applications_export.csv"}
    )


@admin_bp.route('/admin/users')
@login_required
def manage_users():
    """
    Admin view to manage all users (promote/demote).
    Only accessible to admins.
    """
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    users = User.query.order_by(User.full_name).all()
    return render_template('admin/manage_users.html', users=users)



@admin_bp.route('/admin/user/<int:user_id>/promote')
@login_required
def promote_user(user_id):
    """
    Promote a user to admin.
    """
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()

    flash(f"✅ {user.full_name} promoted to admin.", "success")
    return redirect(url_for('admin_bp.manage_users'))


@admin_bp.route('/admin/user/<int:user_id>/demote')
@login_required
def demote_user(user_id):
    """
    Demote a user from admin to regular user.
    Prevent self-demotion for safety.
    """
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('auth.dashboard'))

    user = User.query.get_or_404(user_id)

    # Prevent admin from demoting themselves
    if user.id == current_user.id:
        flash("⚠️ You cannot demote yourself.", "warning")
        return redirect(url_for('admin_bp.manage_users'))

    user.is_admin = False
    db.session.commit()

    flash(f"🧹 {user.full_name} demoted from admin.", "info")
    return redirect(url_for('admin_bp.manage_users'))