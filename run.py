# run.py

from app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler.reminder_scheduler import send_reminder_emails
from app.scheduler.auto_approver import auto_approve_submitted_applications
import atexit

# ✅ Step 1: Create Flask app instance
app = create_app()

# ✅ Step 2: Initialize APScheduler
scheduler = BackgroundScheduler()

# 🔁 Job 1: Send reminder emails every 1 minute (testing mode)
scheduler.add_job(
    func=lambda: send_reminder_emails(app),  # Pass app explicitly
    trigger="interval",
    minutes=1,  # In production: change to `hours=6`
    id='reminder_email_job',
    replace_existing=True
)

# ⏳ Job 2: Auto-approve submitted applications after 24 hours
scheduler.add_job(
    func=lambda: auto_approve_submitted_applications(app),  # Pass app explicitly
    trigger="interval",
     minutes=1,  # In production: change to `hours=1`
    id='auto_approval_job',
    replace_existing=True
)

# Add this to your scheduler setup
scheduler.add_job(
    func=lambda: send_reminder_emails(app),
    trigger="interval",
    days=7,  # Run weekly
    id='reminder_email_job',
    replace_existing=True
)

# ✅ Start the scheduler
scheduler.start()

# 🧼 Ensure the scheduler shuts down gracefully when app stops
atexit.register(lambda: scheduler.shutdown())

# ✅ Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
