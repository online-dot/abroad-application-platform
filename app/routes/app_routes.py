from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, session, flash, current_app, send_from_directory
)
from werkzeug.utils import secure_filename
from datetime import datetime
from app.models.application import Application
from app.models.user import User
from app.models import db
import os

# Define Blueprint for application-related routes
app_bp = Blueprint('app_bp', __name__)

# Helper function to get the currently logged-in user
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


# ---------------------- PASSPORT APPLICATION ROUTES ----------------------
@app_bp.route('/passport-application')
def show_passport_options():
    """Show passport application options with government and express options"""
    user = get_current_user()
    if not user:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('application/passport_options.html')

@app_bp.route('/express-passport', methods=['GET', 'POST'])
def express_passport_application():
    """Handle express passport applications with fast processing"""
    user = get_current_user()
    if not user:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Process form submission
        full_name = request.form.get('full_name')
        id_number = request.form.get('id_number')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Handle file uploads
        photo = request.files.get('photo')
        id_copy = request.files.get('id_copy')

        # Validate inputs
        if not all([full_name, id_number, email, phone, photo, id_copy]):
            flash('Please fill all fields and upload required documents', 'danger')
            return redirect(url_for('app_bp.express_passport_application'))

        # Secure filenames and save
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'passports')
        os.makedirs(upload_folder, exist_ok=True)

        photo_filename = f"photo_{user.id}_{secure_filename(photo.filename)}"
        id_filename = f"id_{user.id}_{secure_filename(id_copy.filename)}"
        
        photo.save(os.path.join(upload_folder, photo_filename))
        id_copy.save(os.path.join(upload_folder, id_filename))

        # Here you would typically:
        # 1. Save to database
        # 2. Process payment
        # 3. Initiate passport application
        
        flash('Your express passport application has been submitted!', 'success')
        return redirect(url_for('app_bp.application_step1'))

    return render_template('application/express_passport.html')


# ---------------------- APPLICATION STEP ROUTES ----------------------
@app_bp.route('/application/step1', methods=['GET', 'POST'])
def application_step1():
    """First step: Passport status check"""
    user = get_current_user()
    if not user:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        passport_status = request.form.get('passport_status')

        if not passport_status:
            flash('Please select your passport status.', 'warning')
            return redirect(url_for('app_bp.application_step1'))

        # Create or update the application
        application = Application.query.filter_by(user_id=user.id).first()
        if not application:
            application = Application(user_id=user.id, passport_status=passport_status)
            db.session.add(application)
        else:
            application.passport_status = passport_status

        db.session.commit()

        # Redirect based on passport status
        if passport_status == 'no_passport':
            return redirect(url_for('app_bp.show_passport_options'))
        else:
            return redirect(url_for('app_bp.application_step2'))

    return render_template('application/step1.html')

@app_bp.route('/application/step2', methods=['GET', 'POST'])
def application_step2():
    """Second step: Personal information collection"""
    user = get_current_user()
    if not user:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('auth.login'))

    application = Application.query.filter_by(user_id=user.id).first()
    if not application:
        flash('Please complete Step 1 first.', 'warning')
        return redirect(url_for('app_bp.application_step1'))

    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        date_of_birth_str = request.form.get('date_of_birth')
        education_level = request.form.get('education_level')
        occupation = request.form.get('occupation')
        marital_status = request.form.get('marital_status')

        # Basic validation
        if not all([phone_number, date_of_birth_str, education_level, occupation, marital_status]):
            flash('Please fill out all fields.', 'warning')
            return redirect(url_for('app_bp.application_step2'))

        # Parse the date string to a date object
        try:
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
            return redirect(url_for('app_bp.application_step2'))

        # Save updated information
        application.phone_number = phone_number
        application.date_of_birth = date_of_birth
        application.education_level = education_level
        application.occupation = occupation
        application.marital_status = marital_status

        db.session.commit()

        flash('Step 2 completed successfully!', 'success')
        return redirect(url_for('app_bp.application_step3'))

    return render_template('application/step2.html')

@app_bp.route('/application/step3', methods=['GET', 'POST'])
def application_step3():
    """Third step: Document uploads"""
    user = get_current_user()
    if not user:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('auth.login'))

    application = Application.query.filter_by(user_id=user.id).first()
    if not application:
        flash('Please complete Step 2 first.', 'warning')
        return redirect(url_for('app_bp.application_step2'))

    if request.method == 'POST':
        cv = request.files.get('cv')
        national_id = request.files.get('national_id')
        certificate = request.files.get('certificate')

        # Validate uploaded files
        if not cv or not national_id or not certificate:
            flash('Please upload all required documents.', 'warning')
            return redirect(url_for('app_bp.application_step3'))

        # Create uploads folder if it doesn't exist
        upload_path = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_path, exist_ok=True)

        # Save each file with a secure name
        cv_filename = secure_filename(cv.filename)
        id_filename = secure_filename(national_id.filename)
        cert_filename = secure_filename(certificate.filename)

        cv.save(os.path.join(upload_path, cv_filename))
        national_id.save(os.path.join(upload_path, id_filename))
        certificate.save(os.path.join(upload_path, cert_filename))

        # Store file names in database
        application.cv_filename = cv_filename
        application.id_filename = id_filename
        application.cert_filename = cert_filename

        db.session.commit()

        flash('Step 3 completed successfully! Documents uploaded.', 'success')
        return redirect(url_for('app_bp.application_step4'))

    return render_template('application/step3.html')

@app_bp.route('/application/step4', methods=['GET', 'POST'])
def application_step4():
    """Fourth step: Final submission"""
    user = get_current_user()
    if not user:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('auth.login'))

    application = Application.query.filter_by(user_id=user.id).first()
    if not application:
        flash('No application found. Please start the application.', 'warning')
        return redirect(url_for('app_bp.application_step1'))

    # Prevent editing after submission
    if application.submitted:
        flash('Your application has already been submitted and cannot be changed.', 'info')
        return redirect(url_for('app_bp.application_summary'))

    if request.method == 'POST':
        # Mark application as submitted
        application.submitted = True
        application.submitted_at = datetime.utcnow()
        db.session.commit()
        
        flash('Application submitted successfully! Thank you.', 'success')
        return redirect(url_for('auth.dashboard'))

    return render_template('application/step4.html', user=user, application=application)

@app_bp.route('/application/summary')
def application_summary():
    """Application summary view"""
    user = get_current_user()
    if not user:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('auth.login'))

    application = Application.query.filter_by(user_id=user.id).first()
    if not application:
        flash('No application found.', 'danger')
        return redirect(url_for('app_bp.application_step1'))

    return render_template('application/summary.html', user=user, application=application)


# ---------------------- FILE SERVING ROUTE ----------------------
@app_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves uploaded files securely"""
    user = get_current_user()
    if not user:
        flash('Please log in to access files.', 'warning')
        return redirect(url_for('auth.login'))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)