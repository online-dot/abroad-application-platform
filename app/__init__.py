import os
from flask import Flask
from app.extensions import db, mail, login_manager
from flask_migrate import Migrate
from app.routes.auth_routes import auth_bp
from app.routes.app_routes import app_bp
from app.routes.admin_routes import admin_bp
from app.models.user import User
from .scheduler.scheduler import start_scheduler
from flask import render_template



migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # --- Configs & Extensions ---
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/job_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'kenyainchiyetu5@gmail.com'
    app.config['MAIL_PASSWORD'] = 'gcmzsribmuoztrgp'
    app.config['MAIL_DEFAULT_SENDER'] = 'kenyainchiyetu5@gmail.com'

    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(app_bp)
    app.register_blueprint(admin_bp)

    start_scheduler(app)

    with app.app_context():
        db.create_all()

    # ✅ ✅ ✅ HOMEPAGE ROUTE — must be BEFORE `return app`
    @app.route('/')
    def index():
        return render_template("home.html")

    print("✅ Registered Routes:")
    print(app.url_map)

    return app
