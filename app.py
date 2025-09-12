import sys
import os
import csv
from datetime import datetime
import uuid
from flask import Flask, request, jsonify, render_template
from ai.client import AIClient
from dotenv import load_dotenv
import atexit

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

load_dotenv()

app = Flask(__name__)

# In-memory storage for chats
# chats = {
#     "chat_id_1": [message1, message2],
#     "chat_id_2": [message3, message4],
# }
chats = {}

# Initialize AI client
# We will create a new AI client for each chat session
# This is because the AIClient is stateful and maintains conversation history
ai_clients = {}

# CSV Logging setup
CSV_FILE = 'data.csv'
CSV_HEADER = ['chat_id', 'timestamp', 'is_ai', 'text']

def load_chats_from_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
        return

    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            if header != CSV_HEADER:
                # Handle old format
                # This is a simple migration, for more complex cases, a migration script would be better
                f.seek(0)
                new_rows = []
                chat_id = str(uuid.uuid4())
                chats[chat_id] = []
                for row in reader:
                    timestamp, is_ai, text = row
                    is_ai = is_ai == 'True'
                    chats[chat_id].append({'timestamp': timestamp, 'is_ai': is_ai, 'text': text})
                    new_rows.append([chat_id, timestamp, is_ai, text])
                
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as fw:
                    writer = csv.writer(fw)
                    writer.writerow(CSV_HEADER)
                    writer.writerows(new_rows)
                return # Exit after migration
        except StopIteration:
            # File is empty
            pass

        # Load new format
        for row in reader:
            chat_id, timestamp, is_ai, text = row
            is_ai = is_ai == 'True'
            if chat_id not in chats:
                chats[chat_id] = []
            chats[chat_id].append({'timestamp': timestamp, 'is_ai': is_ai, 'text': text})

def write_to_csv(data):
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def save_chats_to_csv_on_exit():
    print("Saving all chats to CSV before exit...")
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for chat_id, messages in chats.items():
            for msg in messages:
                writer.writerow([chat_id, msg['timestamp'], msg['is_ai'], msg['text']])
    print("Chats saved.")

atexit.register(save_chats_to_csv_on_exit)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chats', methods=['GET'])
def get_chats():
    return jsonify(list(chats.keys()))

@app.route('/api/chats', methods=['POST'])
def create_chat():
    chat_id = str(uuid.uuid4())
    chats[chat_id] = []
    ai_clients[chat_id] = AIClient(api_key=os.getenv("GEMINI_API_KEY"))
    return jsonify({'chat_id': chat_id})

@app.route('/api/messages/<chat_id>', methods=['GET'])
def get_messages(chat_id):
    return jsonify(chats.get(chat_id, []))

@app.route('/api/messages/<chat_id>', methods=['POST'])
def add_message(chat_id):
    if chat_id not in chats:
        return jsonify({'error': 'Chat not found'}), 404

    print(f"Received message POST for chat {chat_id}: {request.json}")
    
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'Invalid request'}), 400
    
    user_message = {
        'id': str(uuid.uuid4()),
        'text': request.json['text'],
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'is_ai': False
    }
    
    chats[chat_id].append(user_message)
    # write_to_csv([chat_id, user_message['timestamp'], user_message['is_ai'], user_message['text']]) # Removed real-time write
    response_messages = [user_message]
    
    ask_ai = request.json.get('ask_ai', False)
    print(f"Ask AI flag: {ask_ai}")
    
    if ask_ai:
        try:
            if chat_id not in ai_clients:
                ai_clients[chat_id] = AIClient(api_key=os.getenv("GEMINI_API_KEY"))
                # Replay history to the new AI client
                for msg in chats[chat_id]:
                    if not msg['is_ai']:
                        ai_clients[chat_id].get_response(msg['text'])

            ai_text = ai_clients[chat_id].get_response(request.json['text'])
            print(f"AI responded with: {ai_text[:50]}...")
            
            ai_message = {
                'id': str(uuid.uuid4()),
                'text': ai_text,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'is_ai': True
            }
            
            chats[chat_id].append(ai_message)
            # write_to_csv([chat_id, ai_message['timestamp'], ai_message['is_ai'], ai_message['text']]) # Removed real-time write
            response_messages.append(ai_message)
            
        except Exception as e:
            print(f"Error getting AI response: {e}")
    
    return jsonify(response_messages), 201

if __name__ == '__main__':
    load_chats_from_csv()
    app.run(debug=True)