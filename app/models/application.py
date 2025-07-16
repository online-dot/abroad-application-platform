# app/models/application.py

from app.models import db
from datetime import datetime
from app.models.user import User  # Required for user relationship

class Application(db.Model):
    """
    Represents a work abroad application submitted by a user.
    Fields are filled progressively in steps during the application process.
    """

    # -------------------------
    # Core Identifiers
    # -------------------------
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='applications')

    # -------------------------
    # Step 1: Passport Status
    # -------------------------
    passport_status = db.Column(
        db.String(20), 
        nullable=False,
        comment="Passport status: 'has_passport', 'needs_passport', or 'applied_for_passport'"
    )

    # -------------------------
    # Step 2: Personal Details
    # -------------------------
    phone_number = db.Column(
        db.String(20),
        nullable=True,
        comment="User's contact phone number"
    )
    date_of_birth = db.Column(
        db.Date,
        nullable=True,
        comment="User's date of birth in YYYY-MM-DD format"
    )
    education_level = db.Column(
        db.String(50),
        nullable=True,
        comment="Highest education level completed"
    )
    occupation = db.Column(
        db.String(100),
        nullable=True,
        comment="Current or most recent occupation"
    )
    marital_status = db.Column(
        db.String(20),
        nullable=True,
        comment="Marital status: single, married, divorced, etc."
    )

    # -------------------------
    # Step 3: Document Uploads
    # -------------------------
    cv_filename = db.Column(
        db.String(255),
        nullable=True,
        comment="Filename of uploaded CV/resume"
    )
    id_filename = db.Column(
        db.String(255),
        nullable=True,
        comment="Filename of uploaded ID document"
    )
    cert_filename = db.Column(
        db.String(255),
        nullable=True,
        comment="Filename of uploaded education certificate"
    )

    # -------------------------
    # Step 4: Submission & Approval Tracking
    # -------------------------
    submitted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Whether application has been submitted"
    )
    submitted_at = db.Column(
        db.DateTime,
        nullable=True,
        comment="Timestamp when application was submitted"
    )
    approved = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Whether application has been approved"
    )
    approved_at = db.Column(
        db.DateTime,
        nullable=True,
        comment="Timestamp when application was approved"
    )
    last_reminder_sent = db.Column(
        db.DateTime,
        nullable=True,
        comment="Timestamp when last reminder email was sent"
    )

    # -------------------------
    # Instance Methods
    # -------------------------
    def __repr__(self):
        """Official string representation of the application"""
        return f'<Application {self.id} for User {self.user_id}>'

    def get_progress(self):
        """Returns completion percentage of the application"""
        completed = 0
        total = 8  # Total number of required fields
        
        if self.passport_status: completed += 1
        if self.phone_number: completed += 1
        if self.date_of_birth: completed += 1
        if self.education_level: completed += 1
        if self.occupation: completed += 1
        if self.marital_status: completed += 1
        if self.cv_filename and self.id_filename and self.cert_filename: completed += 2
        
        return int((completed / total) * 100)

    def get_registration_number(self):
        """Generates official registration number in format: YYYY + 6-digit ID"""
        return f"{datetime.now().year}{self.id:06d}"

    def is_complete(self):
        """Checks if all required fields are filled"""
        return all([
            self.passport_status,
            self.phone_number,
            self.date_of_birth,
            self.education_level,
            self.occupation,
            self.marital_status,
            self.cv_filename,
            self.id_filename,
            self.cert_filename
        ])