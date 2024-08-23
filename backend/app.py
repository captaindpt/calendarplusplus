import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/api/hello')
def hello():
    app.logger.info("API endpoint /api/hello was called")
    return jsonify({"message": "Hello from the backend!"})

@app.route('/api/status')
def status():
    app.logger.info("API endpoint /api/status was called")
    return jsonify({"status": "Backend is running correctly"})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("Flask server started. Visit http://127.0.0.1:8000 in your browser.")
    app.run(debug=True, port=8000)
