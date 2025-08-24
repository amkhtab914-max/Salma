from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app.main import bp
from app.main.forms import LoginForm, RegistrationForm
from app.models import User, db

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """Serves the main dashboard page, requires login."""
    if current_user.is_admin():
        # Admins can see a different dashboard or be redirected to the admin panel
        return redirect(url_for('admin.dashboard'))

    # Regular clients see the main dashboard
    return render_template('dashboard.html', title='Dashboard')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('main.login'))

        # Check if user is approved by admin
        if not user.is_approved:
            flash('Your account has not been approved by an administrator yet.')
            return redirect(url_for('main.login'))

        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.email}!')
        return redirect(url_for('main.index'))

    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    """Handles user logout."""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        # New users are not approved by default
        user.is_approved = False
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Please wait for admin approval.')
        return redirect(url_for('main.login'))

    return render_template('register.html', title='Register', form=form)
