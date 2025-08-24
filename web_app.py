from flask import Flask, jsonify, render_template, request, abort

# This app object can be imported by a production WSGI server
app = Flask(__name__, template_folder='web/templates', static_folder='web')

# In-memory data store for the latest recommendation.
# This will be updated by the backend script via a POST request.
latest_recommendation = {
    "status": "Waiting for first recommendation from backend script..."
}

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('index.html')

@app.route('/recommendations')
def recommendations_page():
    """Serves the historical recommendations page."""
    return render_template('pages/recommendations.html')

@app.route('/api/latest_recommendation', methods=['GET'])
def get_latest_recommendation():
    """
    Public API endpoint for the frontend to fetch the latest recommendation.
    """
    return jsonify(latest_recommendation)

@app.route('/api/internal/update_recommendation', methods=['POST'])
def update_recommendation():
    """
    Internal-only API endpoint for the backend script to push new recommendations.
    """
    # Basic security: only allow requests from localhost
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden

    global latest_recommendation
    new_data = request.json
    if not new_data:
        abort(400) # Bad request

    latest_recommendation = new_data
    print(f"Web app received new recommendation: {new_data.get('decision')}")
    return jsonify({"status": "success", "message": "Recommendation updated."})


def run_web_server():
    """
    Function to run the web server.
    """
    # Note: The user should use a production WSGI server like Gunicorn or Waitress
    # instead of Flask's built-in development server for a real deployment.
    print("Starting Flask web server...")
    app.run(host='0.0.0.0', port=8080, debug=False)


if __name__ == '__main__':
    # This allows running the web app directly for testing.
    run_web_server()
