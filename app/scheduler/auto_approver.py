from datetime import datetime, timedelta
from app.models.application import Application
from app.models import db
from flask import current_app
from utils.email_utils import send_acceptance_email

def auto_approve_submitted_applications(app):
    """
    Automatically approves submitted applications that are over 24 hours old
    and sends acceptance emails.
    """
    with app.app_context():
        current_app.logger.info("⏳ Running auto-approval job...")
        now = datetime.utcnow()
        
        # Find applications ready for auto-approval
        applications = Application.query.filter(
            Application.submitted == True,
            Application.approved == False,
            Application.submitted_at <= now - timedelta(hours=24)
        ).all()

        approval_count = 0
        
        for app_obj in applications:
            try:
                # Approve application
                app_obj.approved = True
                app_obj.approved_at = now
                app_obj.last_reminder_sent = now  # Initialize reminder tracking
                db.session.commit()
                
                # Send acceptance email
                registration_number = f"2025{app_obj.id:06d}"
                success, message = send_acceptance_email(
                    to_email=app_obj.user.email,
                    user_name=app_obj.user.full_name,
                    registration_number=registration_number
                )
                
                if success:
                    current_app.logger.info(f"✅ Sent acceptance email to {app_obj.user.email}")
                    approval_count += 1
                else:
                    current_app.logger.error(f"❌ Failed to send email to {app_obj.user.email}: {message}")
                    
            except Exception as e:
                current_app.logger.error(f"❌ Error processing application {app_obj.id}: {str(e)}")
                db.session.rollback()

        current_app.logger.info(f"✅ Auto-approval job completed. Approved {approval_count} applications.")
        return f"Approved {approval_count} applications"