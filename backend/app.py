import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from schedule_processor import ScheduleProcessor
import asyncio
from functools import partial
import json
from datetime import datetime
import logging

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__, static_folder='../frontend/build')
app.json_encoder = CustomJSONEncoder  # Use our custom encoder
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 3600
    }
})

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the ScheduleProcessor with the API key
api_key = os.getenv('OPENAI_API_KEY')
processor = ScheduleProcessor(api_key)

def run_async(func):
    """Helper function to run async functions in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(func)
    loop.close()
    return result

@app.route('/api/hello')
def hello():
    app.logger.info("API endpoint /api/hello was called")
    return jsonify({"message": "Hello from the backend!"})

@app.route('/api/status')
def status():
    app.logger.info("API endpoint /api/status was called")
    return jsonify({"status": "Backend is running correctly"})

@app.route('/api/log', methods=['POST'])
def log_ics_processing():
    """Endpoint to log ICS processing events from frontend"""
    try:
        log_data = request.json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create logs/frontend_ics_logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'frontend_ics_logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file
        filename = f'ics_processing_{timestamp}.json'
        filepath = os.path.join(log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Logged ICS processing event to: {filepath}")
        return jsonify({"status": "success", "file": filepath})
    except Exception as e:
        logger.error(f"Error logging ICS processing: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/process-schedule', methods=['POST'])
def process_schedule():
    """Process a schedule description and return ICS content"""
    try:
        data = request.get_json()
        if not data or 'schedule' not in data:
            logger.error("No schedule provided in request")
            return jsonify({"error": "No schedule provided"}), 400
            
        schedule_text = data['schedule']
        logger.info(f"Processing schedule request: {schedule_text}")
        
        try:
            # Use run_async to handle the async call
            logger.info("Starting async processing")
            ics_content = run_async(processor.process_user_schedule(schedule_text))
            logger.info("Async processing completed")
            
            # Ensure proper datetime serialization in the response
            logger.info("Serializing response")
            if isinstance(ics_content, dict):
                logger.debug("Converting dict response to JSON")
                ics_content = json.loads(json.dumps(ics_content, cls=CustomJSONEncoder))
            elif isinstance(ics_content, str):
                logger.debug("Response is already a string (ICS format)")
                pass
            else:
                logger.debug(f"Converting {type(ics_content)} response to JSON")
                ics_content = json.loads(json.dumps(ics_content, cls=CustomJSONEncoder))
            
            logger.info("Successfully processed schedule")
            return jsonify({"ics_content": ics_content})
            
        except Exception as e:
            logger.error(f"Error during schedule processing: {str(e)}", exc_info=True)
            if "ValidationError" in str(e) or "RetryError" in str(e):
                return jsonify({
                    "error": "Failed to understand the schedule format. Please try rephrasing your schedule description.",
                    "details": str(e)
                }), 422
            raise
            
    except Exception as e:
        logger.error(f"Unexpected error in process_schedule: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Failed to process schedule",
            "details": str(e)
        }), 500

@app.route('/api/process-audio', methods=['POST'])
def process_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        if not audio_file.filename:
            return jsonify({'error': 'No selected file'}), 400
            
        # Save temporarily
        temp_path = os.path.join(app.root_path, 'temp_audio.wav')
        audio_file.save(temp_path)
        
        try:
            # Process audio in sync context
            transcript = run_async(processor.transcribe_audio(temp_path))
            ics_content = run_async(processor.process_user_schedule(transcript))
            
            return jsonify({
                'transcript': transcript,
                'ics_content': ics_content
            })
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        app.logger.error(f"Error processing audio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=8001, debug=True)
    print("Flask server is running at http://localhost:8001")
