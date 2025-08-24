from flask import Flask
from config import Config
from app.extensions import db, migrate, login

def create_app(config_class=Config):
    """
    Application factory function.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # This tells Flask-Login which view to redirect to for login
    login.login_view = 'main.login'

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # The following is needed to create the database tables
    with app.app_context():
        # Import models here so that they are registered with SQLAlchemy
        from app import models
        # This will create the tables if they don't exist, based on the models.
        # For production, we would use Flask-Migrate to manage changes.
        db.create_all()

    # Flask-Login user loader
    @login.user_loader
    def load_user(id):
        from app.models import User
        return User.query.get(int(id))

    @app.shell_context_processor
    def make_shell_context():
        # Makes these items available in `flask shell` for easy testing
        return {'db': db, 'User': models.User}

    return app
