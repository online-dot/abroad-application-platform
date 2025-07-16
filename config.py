import os

class Config:
    SECRET_KEY = 'd1a2e5f8c4b9d7e3f29b7f81a8c5d6e94a0b3c2e10f1a2b3d4e5f6a7b8c9d0e1'  # ✅ Replace this with a long random key

    # ✅ Use your database folder cleanly
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/job_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Gmail Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kenyainchiyetu5@gmail.com'
    MAIL_PASSWORD = 'gcmzsribmuoztrgp'  # ✅ Gmail App Password
    MAIL_DEFAULT_SENDER = ('Work Abroad Team', 'kenyainchiyetu5@gmail.com')
