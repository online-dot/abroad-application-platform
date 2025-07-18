from app import create_app
from app.models import db
from app.models.user import User

app = create_app()

with app.app_context():
    email_to_delete = "onyangovincent200@gmail.com"  # 🔁 Change this

    user = User.query.filter_by(email=email_to_delete).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"✅ Deleted user: {email_to_delete}")
    else:
        print("❌ No user found with that email.")
