from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from app.extensions import db

class User(UserMixin, db.Model):
    """User model for storing user accounts."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), default='client') # 'client' or 'admin'

    # Fields for user management
    is_active = db.Column(db.Boolean, default=True) # For Flask-Login
    is_approved = db.Column(db.Boolean, default=False) # For admin approval

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Checks if the user has the admin role."""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email}>'
