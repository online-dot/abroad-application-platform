from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.application import Application
from app.models import db
from datetime import datetime
from utils.email_utils import send_email  

auth_bp = Blueprint('auth', __name__)

def after_login_redirect():
    """
    Helper function to redirect the logged-in user
    to the appropriate application step based on progress.
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    application = Application.query.filter_by(user_id=user_id).first()

    if not application or not application.passport_status:
        return redirect(url_for('app_bp.application_step1'))

    if not all([
        application.phone_number,
        application.date_of_birth,
        application.education_level,
        application.occupation,
        application.marital_status
    ]):
        return redirect(url_for('app_bp.application_step2'))

    if not all([
        application.cv_filename,
        application.id_filename,
        application.cert_filename
    ]):
        return redirect(url_for('app_bp.application_step3'))

    if not getattr(application, 'submitted', False):
        return redirect(url_for('app_bp.application_step4'))

    return redirect(url_for('app_bp.application_summary'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not full_name or not email or not password:
            flash('Please fill out all fields.', 'warning')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        new_user = User(full_name=full_name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # ✅ Send welcome email
        subject = "Welcome to the Work Abroad Application Platform"
        recipients = [email]
        body = f"""
Hello {full_name},

Thank you for registering on our platform.

You can now log in and complete your application.

Best regards,
Work Abroad Team
"""
        success, message = send_email(subject, recipients, body)

        if success:
            flash('Registration successful! Confirmation email sent.', 'success')
        else:
            flash(f'Registration successful, but email failed: {message}', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login and redirects based on 'next' query param
    or application progress if none provided.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        next_page = request.args.get('next')  # ✅ Optional redirect target

        if not email or not password:
            flash('Please fill out both email and password.', 'warning')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # ✅ Flask-Login session
            login_user(user)

            # ✅ Also store custom session data (optional)
            session['user_id'] = user.id
            session['user_name'] = user.full_name

            flash('Login successful!', 'success')

            # ✅ Redirect to next page if available, otherwise normal dashboard flow
            return redirect(next_page or url_for('auth.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard after login: shows progress and links to next step.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    application = Application.query.filter_by(user_id=user_id).first()

    # Track step progress
    steps = {
        'step1': False,
        'step2': False,
        'step3': False,
        'step4': False,
    }

    if application:
        steps['step1'] = bool(application.passport_status)
        steps['step2'] = all([
            application.phone_number,
            application.date_of_birth,
            application.education_level,
            application.occupation,
            application.marital_status
        ])
        steps['step3'] = all([
            application.cv_filename,
            application.id_filename,
            application.cert_filename
        ])
        steps['step4'] = getattr(application, 'submitted', False)

    if not steps['step1']:
        next_step_url = url_for('app_bp.application_step1')
    elif not steps['step2']:
        next_step_url = url_for('app_bp.application_step2')
    elif not steps['step3']:
        next_step_url = url_for('app_bp.application_step3')
    elif not steps['step4']:
        next_step_url = url_for('app_bp.application_step4')
    else:
        next_step_url = url_for('app_bp.application_summary')

    return render_template(
        'dashboard.html',
        user=user,
        application=application,
        steps=steps,
        next_step_url=next_step_url
    )


@auth_bp.route('/logout')
def logout():
    """
    Clears session and logs user out using Flask-Login.
    """
    session.clear()
    logout_user()  # ✅ Flask-Login logout
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
