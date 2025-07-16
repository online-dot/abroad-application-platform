from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app

from app.scheduler.auto_approver import auto_approve_submitted_applications

# Create a BackgroundScheduler instance globally
scheduler = BackgroundScheduler()

def start_scheduler(app):
    """
    Starts the APScheduler with the Flask app context.
    Schedules periodic jobs like auto-approval of submitted applications.
    """
    with app.app_context():
        # Schedule the auto-approval job to run every hour
        scheduler.add_job(
            func=lambda: auto_approve_submitted_applications(app),
            trigger='interval',
            hours=1,
            id='auto_approval_job',  # optional job id for reference
            replace_existing=True    # replace job if it already exists
        )

        # TODO: Add other scheduled jobs like reminder emails here if needed

        # Start the scheduler if not already running
        if not scheduler.running:
            scheduler.start()
            current_app.logger.info("Scheduler started - auto-approval job scheduled every hour")

        # Optional: Cleanly shutdown scheduler when app context tears down
        @app.teardown_appcontext
        def shutdown_scheduler(exception=None):
            if scheduler.running:
                scheduler.shutdown(wait=False)
                current_app.logger.info("Scheduler shut down on app context teardown")
