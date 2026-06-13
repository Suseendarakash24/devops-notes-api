import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database for simplicity (Use PostgreSQL in real DevOps)
notes = []

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running!"})

@app.route('/notes', methods=['GET'])
def get_notes():
    return jsonify(notes)

@app.route('/notes', methods=['POST'])
def add_note():
    data = request.json
    notes.append(data)
    return jsonify({"message": "Note added!", "note": data}), 201

if __name__ == '__main__':
    # Dynamically get the port from Render's environment variable
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port)