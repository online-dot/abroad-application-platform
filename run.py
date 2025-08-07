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
print("📅 Registering frequent reminder email job...")
scheduler.add_job(
    func=lambda: print(send_reminder_emails(app)),  # Log result in terminal
    trigger="interval",
    minutes=1,
    id='reminder_email_job_frequent',
    replace_existing=True
)

# ⏳ Job 2: Auto-approve submitted applications after 24 hours
print("📅 Registering auto approval job...")
scheduler.add_job(
    func=lambda: print(auto_approve_submitted_applications(app)),  # Log result
    trigger="interval",
    minutes=1,
    id='auto_approval_job',
    replace_existing=True
)

# 📅 Job 3: Weekly reminder emails
print("📅 Registering weekly reminder job...")
scheduler.add_job(
    func=lambda: print(send_reminder_emails(app)),  # Log result
    trigger="interval",
    minutes=1,
    id='reminder_email_job_weekly',
    replace_existing=True
)

# ✅ Start the scheduler (only once!)
scheduler.start()
print("✅ APScheduler started!")

# 🧼 Ensure the scheduler shuts down gracefully when app stops
atexit.register(lambda: scheduler.shutdown())

# ✅ Run Flask app
if __name__ == '__main__':
    # Prevent scheduler from running twice
    app.run(debug=True, use_reloader=False, threaded=True)
