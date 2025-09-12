import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from flask import Flask, request, jsonify, render_template
from datetime import datetime
import uuid
from ai.client import AIClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# In-memory storage for messages
messages = []

# Initialize AI client
ai_client = AIClient(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

@app.route('/api/messages', methods=['POST'])
def add_message():
    print(f"Received message POST: {request.json}")
    
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    user_message = {
        'id': str(uuid.uuid4()),
        'text': request.json['text'],
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'is_ai': False
    }
    
    messages.append(user_message)
    response_messages = [user_message]
    
    # Check if AI should respond
    ask_ai = request.json.get('ask_ai', False)
    print(f"Ask AI flag: {ask_ai}")
    
    if ask_ai:
        try:
            # Get AI response
            ai_text = ai_client.get_response(request.json['text'])
            print(f"AI responded with: {ai_text[:50]}...")
            
            # Create AI message
            ai_message = {
                'id': str(uuid.uuid4()),
                'text': ai_text,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'is_ai': True
            }
            
            messages.append(ai_message)
            response_messages.append(ai_message)
            
        except Exception as e:
            print(f"Error getting AI response: {e}")
    
    return jsonify(response_messages), 201

if __name__ == '__main__':
    app.run(debug=True)