from datetime import datetime, timedelta
from app.models.application import Application
from app.models import db
from flask import current_app, render_template
from utils.email_utils import send_acceptance_email, send_email
from app.models.user import User

def send_reminder_emails(app):
    with app.app_context():
        current_app.logger.info("🔄 Running reminder email job...")
        now = datetime.utcnow()
        reminder_stats = {
            'no_application': 0,
            'incomplete': 0,
            'approved': 0,
            'errors': 0
        }

        users = User.query.all()
        for user in users:
            try:
                application = Application.query.filter_by(user_id=user.id).first()

                # CASE 1: No application at all
                if not application:
                    subject = "📩 Reminder: Start Your Work Abroad Application"
                    recipients = [user.email]

                    html_body = render_template(
                        "emails/no_application_reminder.html",
                        full_name=user.full_name
                    )

                    text_body = f"""Hello {user.full_name},

We noticed you created an account but haven't started your Work Abroad application yet.

Start here: http://yourwebsite.com/login

- Work Abroad Team
"""

                    success, msg = send_email(subject, recipients, text_body, html=html_body)
                    if success:
                        current_app.logger.info(f"✅ Sent no-application reminder to {user.email}")
                        reminder_stats['no_application'] += 1
                    else:
                        current_app.logger.error(f"❌ Failed to send no-application reminder to {user.email}: {msg}")
                        reminder_stats['errors'] += 1

                    continue  # Move to next user after sending

                # CASE 2: Incomplete application
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
                    incomplete.append("Step 3: Upload Documents")
                if not getattr(application, 'submitted', False):
                    incomplete.append("Step 4: Final Submission")

                if incomplete:
                    subject = "⏳ Reminder: Complete Your Work Abroad Application"
                    steps = "\n- " + "\n- ".join(incomplete)
                    body = f"""Hello {user.full_name},

Your application is still incomplete. Please complete:
{steps}

Resume here: http://yourwebsite.com/login
"""
                    success, msg = send_email(subject, [user.email], body)
                    if success:
                        current_app.logger.info(f"✅ Sent incomplete reminder to {user.email}")
                        reminder_stats['incomplete'] += 1
                    else:
                        current_app.logger.error(f"❌ Failed to send incomplete reminder to {user.email}: {msg}")
                        reminder_stats['errors'] += 1

            except Exception as e:
                current_app.logger.error(f"❌ Error processing user {user.email}: {str(e)}")
                reminder_stats['errors'] += 1

        # CASE 3: Weekly reminder for approved applications
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
                    current_app.logger.info(f"✅ Sent weekly approval reminder to {app_obj.user.email}")
                    reminder_stats['approved'] += 1
                else:
                    current_app.logger.error(f"❌ Failed to send approval reminder to {app_obj.user.email}: {message}")
                    reminder_stats['errors'] += 1
            except Exception as e:
                current_app.logger.error(f"❌ Error sending weekly reminder: {str(e)}")
                db.session.rollback()
                reminder_stats['errors'] += 1

        # ✅ Summary log
        current_app.logger.info(
            f"✅ Reminder job completed.\n"
            f"🔹 No Application: {reminder_stats['no_application']}\n"
            f"🔹 Incomplete: {reminder_stats['incomplete']}\n"
            f"🔹 Approved Weekly: {reminder_stats['approved']}\n"
            f"🔺 Errors: {reminder_stats['errors']}"
        )
        return reminder_stats
