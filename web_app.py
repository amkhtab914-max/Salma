from flask import Flask, jsonify, render_template
import threading

# This app object will be imported by the main run.py
# We specify the template_folder for HTML files and a static_folder for CSS/JS files.
app = Flask(__name__, template_folder='web/templates', static_folder='web')

# A simple dictionary to hold a reference to the shared data object
# This will be set by the main thread before the app is run.
app.config['SHARED_DATA'] = {
    "latest_recommendation": None,
    "lock": threading.Lock()
}

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('index.html')

@app.route('/recommendations')
def recommendations_page():
    """Serves the historical recommendations page."""
    # Note: We need to specify the path relative to the template_folder
    return render_template('pages/recommendations.html')

@app.route('/api/latest_recommendation')
def get_latest_recommendation():
    """API endpoint to get the latest recommendation."""
    shared_data = app.config['SHARED_DATA']
    with shared_data["lock"]:
        if shared_data["latest_recommendation"]:
            return jsonify(shared_data["latest_recommendation"])
        else:
            return jsonify({"status": "no recommendation available yet"}), 404

def run_web_server(shared_data_ref):
    """
    Function to run the web server, to be called in a thread.
    It updates the app's config with the actual shared data object.
    """
    app.config['SHARED_DATA'] = shared_data_ref
    # use_reloader=False is important for running in a thread
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

if __name__ == '__main__':
    # This block is for testing the web app in isolation.
    print("--- Running Web App in standalone test mode ---")
    # A dummy shared_data object for the test
    test_shared_data = {
        "latest_recommendation": {
            "confidence": 75.5,
            "decision": "BUY",
            "scenario": "This is a test scenario for the web interface.",
            "individual_scores": {
                "Momentum": {"score": 0.8, "rationale": "Test rationale"},
                "ATR_Filter": {"score": 0.6, "rationale": "Test rationale 2"}
            }
        },
        "lock": threading.Lock()
    }
    run_web_server(test_shared_data)
