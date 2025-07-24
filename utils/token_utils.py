from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_reset_token(email, expires_sec=1800):  # 30 minutes
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='password-reset')

def verify_reset_token(token, expires_sec=1800):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset', max_age=expires_sec)
    except Exception:
        return None
    return email
