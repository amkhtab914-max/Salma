"""
This file initializes the Flask extensions.
By keeping them in a separate file, we avoid circular import issues.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
