from datetime import datetime, timedelta
from app.models.application import Application
from app.models import db
from flask import current_app
from utils.email_utils import send_acceptance_email

def send_reminder_emails(app):
    """
    Sends two types of reminders:
    1. For incomplete applications (original functionality)
    2. For approved applications with no recent activity (new functionality)
    """
    with app.app_context():
        current_app.logger.info("🔄 Running reminder email job...")
        now = datetime.utcnow()
        reminder_stats = {
            'incomplete': 0,
            'approved': 0,
            'errors': 0
        }

        # 1. Reminders for incomplete applications
        users = User.query.all()
        for user in users:
            application = Application.query.filter_by(user_id=user.id).first()
            if not application:
                continue

            # Check for incomplete steps
            incomplete = []
            if not application.passport_status:
                incomplete.append("Step 1: Passport info")
            if not all([
                application.phone_number,
                application.date_of_birth,
                application.education_level,
                application.occupation,
                application.marital_status
            ]):
                incomplete.append("Step 2: Personal Details")
            if not all([
                application.cv_filename,
                application.id_filename,
                application.cert_filename
            ]):
                incomplete.append("Step 3: Documents")
            if not getattr(application, 'submitted', False):
                incomplete.append("Step 4: Final Submission")

            if incomplete:
                try:
                    subject = "⏳ Reminder: Complete Your Work Abroad Application"
                    recipients = [user.email]
                    steps = "\n- " + "\n- ".join(incomplete)

                    body = f"""Hello {user.full_name},

We noticed your application is still incomplete. Please complete:
{steps}

Resume your application: http://yourwebsite.com/login
"""
                    success, msg = send_email(subject, recipients, body)
                    if success:
                        current_app.logger.info(f"✅ Sent incomplete reminder to {user.email}")
                        reminder_stats['incomplete'] += 1
                    else:
                        current_app.logger.error(f"❌ Failed to send incomplete reminder: {msg}")
                        reminder_stats['errors'] += 1
                except Exception as e:
                    current_app.logger.error(f"❌ Error sending incomplete reminder: {str(e)}")
                    reminder_stats['errors'] += 1

        # 2. Reminders for approved applications (new functionality)
        approved_apps = Application.query.filter(
            Application.approved == True,
            Application.last_reminder_sent <= now - timedelta(days=7)
        ).all()

        for app_obj in approved_apps:
            try:
                registration_number = f"2025{app_obj.id:06d}"
                success, message = send_acceptance_email(
                    to_email=app_obj.user.email,
                    user_name=app_obj.user.full_name,
                    registration_number=registration_number,
                    is_reminder=True
                )
                
                if success:
                    app_obj.last_reminder_sent = now
                    db.session.commit()
                    current_app.logger.info(f"✅ Sent approval reminder to {app_obj.user.email}")
                    reminder_stats['approved'] += 1
                else:
                    current_app.logger.error(f"❌ Failed to send approval reminder: {message}")
                    reminder_stats['errors'] += 1
                    
            except Exception as e:
                current_app.logger.error(f"❌ Error sending approval reminder: {str(e)}")
                reminder_stats['errors'] += 1
                db.session.rollback()

        current_app.logger.info(
            f"✅ Reminder job completed. "
            f"Incomplete: {reminder_stats['incomplete']}, "
            f"Approved: {reminder_stats['approved']}, "
            f"Errors: {reminder_stats['errors']}"
        )
        return reminder_stats