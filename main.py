from app import create_app, db
from app.models import User
import os

# Create the Flask app instance using the factory
app = create_app()

def create_initial_data(app_context):
    """Create a default admin user if one doesn't exist."""
    with app_context:
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')

        # Check if admin user exists
        if User.query.filter_by(role='admin').first() is None:
            print(f"Creating default admin user: {admin_email}")
            admin_user = User(email=admin_email, role='admin', is_approved=True, is_active=True)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")

if __name__ == '__main__':
    # Create an app context to interact with the database
    create_initial_data(app.app_context())

    # Run the app
    # The user should use a production WSGI server in a real deployment
    app.run(host='0.0.0.0', port=8080, debug=False)
