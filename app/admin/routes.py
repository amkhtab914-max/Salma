from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.admin import bp

def admin_required(f):
    """
    Decorator to ensure a user is logged in and has the 'admin' role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

from flask import render_template
from app.models import User

@bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard page, shows a list of all users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/dashboard.html', users=users, title="Admin Dashboard")

@bp.route('/approve/<int:user_id>')
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f'User {user.email} has been approved.')
    return redirect(url_for('admin.dashboard'))

@bp.route('/deactivate/<int:user_id>')
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    # You should not be able to deactivate yourself
    if user.id == current_user.id:
        flash('You cannot deactivate yourself.')
        return redirect(url_for('admin.dashboard'))
    user.is_active = False
    db.session.commit()
    flash(f'User {user.email} has been deactivated.')
    return redirect(url_for('admin.dashboard'))

@bp.route('/activate/<int:user_id>')
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(f'User {user.email} has been activated.')
    return redirect(url_for('admin.dashboard'))
