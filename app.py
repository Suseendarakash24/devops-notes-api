from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)

# In-memory database with sample data
notes = [
    {
        "id": 1,
        "title": "Welcome to DevOps Notes API",
        "content": "This is a cloud-native application deployed using Docker, GitHub Actions, and Render!",
        "category": "DevOps",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

next_id = 2

# ===== HOMEPAGE WITH FULL UI =====
@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DevOps Notes Manager</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 30px;
                text-align: center;
            }
            .header h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .status-badge {
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                font-size: 14px;
                margin: 10px 0;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                text-align: center;
            }
            .stat-card h3 {
                color: #667eea;
                font-size: 2em;
                margin-bottom: 5px;
            }
            .stat-card p {
                color: #666;
                font-size: 14px;
            }
            .main-content {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 30px;
            }
            .form-section, .notes-section {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .form-section h2, .notes-section h2 {
                color: #667eea;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #f0f0f0;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }
            .form-group input,
            .form-group textarea,
            .form-group select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            .form-group input:focus,
            .form-group textarea:focus,
            .form-group select:focus {
                outline: none;
                border-color: #667eea;
            }
            .form-group textarea {
                resize: vertical;
                min-height: 120px;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                width: 100%;
                transition: background 0.3s;
            }
            .btn:hover {
                background: #764ba2;
            }
            .btn-danger {
                background: #dc3545;
                padding: 8px 15px;
                font-size: 14px;
                width: auto;
            }
            .btn-danger:hover {
                background: #c82333;
            }
            .search-box {
                margin-bottom: 20px;
            }
            .search-box input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
            }
            .note-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
                transition: transform 0.3s;
            }
            .note-card:hover {
                transform: translateX(5px);
            }
            .note-card h3 {
                color: #333;
                margin-bottom: 10px;
            }
            .note-card p {
                color: #666;
                line-height: 1.6;
                margin-bottom: 10px;
            }
            .note-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 15px;
            }
            .category-badge {
                background: #667eea;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 12px;
            }
            .timestamp {
                color: #999;
                font-size: 12px;
            }
            .no-notes {
                text-align: center;
                color: #999;
                padding: 40px;
                font-style: italic;
            }
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1>🚀 DevOps Notes Manager</h1>
                <div class="status-badge">✅ API is Live & Running</div>
                <p style="margin-top: 10px; color: #666;">
                    A cloud-native application deployed with Docker, GitHub Actions & Render
                </p>
            </div>

            <!-- Stats -->
            <div class="stats">
                <div class="stat-card">
                    <h3 id="totalNotes">{{ total_notes }}</h3>
                    <p>Total Notes</p>
                </div>
                <div class="stat-card">
                    <h3 id="totalCategories">{{ total_categories }}</h3>
                    <p>Categories</p>
                </div>
                <div class="stat-card">
                    <h3>DevOps</h3>
                    <p>Project Type</p>
                </div>
            </div>

            <!-- Main Content -->
            <div class="main-content">
                <!-- Add Note Form -->
                <div class="form-section">
                    <h2>📝 Add New Note</h2>
                    <form method="POST" action="/notes">
                        <div class="form-group">
                            <label for="title">Title *</label>
                            <input type="text" id="title" name="title" required 
                                   placeholder="Enter note title">
                        </div>
                        <div class="form-group">
                            <label for="category">Category</label>
                            <select id="category" name="category">
                                <option value="General">General</option>
                                <option value="DevOps">DevOps</option>
                                <option value="Programming">Programming</option>
                                <option value="Cloud">Cloud</option>
                                <option value="Database">Database</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="content">Content *</label>
                            <textarea id="content" name="content" required 
                                      placeholder="Write your note here..."></textarea>
                        </div>
                        <button type="submit" class="btn">➕ Add Note</button>
                    </form>

                    <hr style="margin: 30px 0; border: none; border-top: 2px solid #f0f0f0;">
                    
                    <h3 style="color: #667eea; margin-bottom: 15px;">🔧 API Endpoints</h3>
                    <ul style="list-style: none; color: #666; line-height: 2;">
                        <li>✅ GET <a href="/health" style="color: #667eea;">/health</a> - Health Check</li>
                        <li>✅ GET <a href="/notes" style="color: #667eea;">/notes</a> - Get All Notes (JSON)</li>
                        <li>✅ POST <code style="background: #f0f0f0; padding: 2px 8px; border-radius: 4px;">/notes</code> - Add Note</li>
                        <li>✅ DELETE <code style="background: #f0f0f0; padding: 2px 8px; border-radius: 4px;">/notes/&lt;id&gt;</code> - Delete Note</li>
                    </ul>
                </div>

                <!-- Notes List -->
                <div class="notes-section">
                    <h2>📋 All Notes</h2>
                    
                    <!-- Search Box -->
                    <div class="search-box">
                        <input type="text" id="searchInput" placeholder="🔍 Search notes by title or content..." 
                               onkeyup="searchNotes()">
                    </div>

                    <div id="notesList">
                        {% if notes %}
                            {% for note in notes %}
                            <div class="note-card" data-title="{{ note.title.lower() }}" data-content="{{ note.content.lower() }}">
                                <h3>{{ note.title }}</h3>
                                <p>{{ note.content }}</p>
                                <div class="note-meta">
                                    <span class="category-badge">{{ note.category }}</span>
                                    <div>
                                        <span class="timestamp">{{ note.created_at }}</span>
                                        <form method="POST" action="/notes/{{ note.id }}/delete" style="display: inline; margin-left: 10px;">
                                            <button type="submit" class="btn btn-danger" 
                                                    onclick="return confirm('Delete this note?')">🗑️ Delete</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <div class="no-notes">
                                <p>📭 No notes yet. Add your first note using the form!</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <script>
            function searchNotes() {
                const input = document.getElementById('searchInput').value.toLowerCase();
                const notes = document.querySelectorAll('.note-card');
                
                notes.forEach(note => {
                    const title = note.getAttribute('data-title');
                    const content = note.getAttribute('data-content');
                    
                    if (title.includes(input) || content.includes(input)) {
                        note.style.display = 'block';
                    } else {
                        note.style.display = 'none';
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    
    # Get unique categories
    categories = set(note['category'] for note in notes)
    
    return render_template_string(html, 
                                  notes=notes, 
                                  total_notes=len(notes),
                                  total_categories=len(categories))

# ===== API ENDPOINTS =====
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "DevOps Notes API is running!",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/notes', methods=['GET'])
def get_notes():
    return jsonify(notes)

@app.route('/notes', methods=['POST'])
def add_note():
    global next_id
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.json
    else:
        data = request.form
    
    new_note = {
        "id": next_id,
        "title": data.get('title', 'Untitled'),
        "content": data.get('content', ''),
        "category": data.get('category', 'General'),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    notes.append(new_note)
    next_id += 1
    
    # If form submission, redirect to homepage
    if not request.is_json:
        return redirect(url_for('home'))
    
    return jsonify({"message": "Note added successfully!", "note": new_note}), 201

@app.route('/notes/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    global notes
    notes = [note for note in notes if note['id'] != note_id]
    return redirect(url_for('home'))

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note_api(note_id):
    global notes
    original_count = len(notes)
    notes = [note for note in notes if note['id'] != note_id]
    
    if len(notes) < original_count:
        return jsonify({"message": "Note deleted successfully!"}), 200
    else:
        return jsonify({"error": "Note not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)