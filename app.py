from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)

# In-memory database
notes = [
    {"id": 1, "title": "Welcome Note", "content": "This is your DevOps API!"}
]

# ===== HOMEPAGE WITH HTML UI =====
@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevOps Notes API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 { color: #667eea; text-align: center; }
            .note {
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }
            .note h3 { margin: 0 0 10px 0; color: #333; }
            .note p { margin: 0; color: #666; }
            form {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 5px;
            }
            input, textarea {
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover { background: #764ba2; }
            .status { 
                display: inline-block; 
                padding: 5px 10px; 
                background: #28a745; 
                color: white; 
                border-radius: 5px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 DevOps Notes API</h1>
            <div style="text-align: center;">
                <span class="status">✅ API is Live & Running</span>
            </div>
            
            <h2>📝 Existing Notes:</h2>
            {% for note in notes %}
            <div class="note">
                <h3>{{ note.title }}</h3>
                <p>{{ note.content }}</p>
            </div>
            {% endfor %}
            
            <form method="POST" action="/notes">
                <h3>Add New Note:</h3>
                <input type="text" name="title" placeholder="Note Title" required>
                <textarea name="content" rows="4" placeholder="Note Content" required></textarea>
                <button type="submit">➕ Add Note</button>
            </form>
            
            <hr style="margin: 30px 0;">
            <p style="text-align: center; color: #666;">
                <strong>API Endpoints:</strong><br>
                GET /health - Health Check<br>
                GET /notes - Get all notes (JSON)<br>
                POST /notes - Add new note
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, notes=notes)

# ===== API ENDPOINTS =====
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running!"})

@app.route('/notes', methods=['GET'])
def get_notes():
    return jsonify(notes)

@app.route('/notes', methods=['POST'])
def add_note():
    # Handle both JSON and form data
    if request.is_json:
        data = request.json
    else:
        data = request.form
    
    new_note = {
        "id": len(notes) + 1,
        "title": data.get('title', 'Untitled'),
        "content": data.get('content', '')
    }
    notes.append(new_note)
    
    # If form submission, redirect to homepage
    if not request.is_json:
        return render_template_string('<script>window.location.href="/"</script>')
    
    return jsonify({"message": "Note added!", "note": new_note}), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)