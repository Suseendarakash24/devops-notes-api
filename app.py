from flask import Flask, render_template_string, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_change_this_in_production')

# ===== SQLite Database Configuration =====
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='General')
    pinned = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Templates ---
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - Notes App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; height: 100vh; font-family: 'Segoe UI', sans-serif; }
        .auth-card { width: 100%; max-width: 400px; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .btn-primary { background: #4f46e5; border: none; padding: 10px; font-weight: 600; }
        .btn-primary:hover { background: #4338ca; }
        .form-control { padding: 12px; border-radius: 8px; border: 1px solid #e5e7eb; }
        .form-control:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
    </style>
</head>
<body>
    <div class="auth-card">
        <h3 class="text-center mb-4 fw-bold text-dark"><i class="bi bi-journal-richtext me-2"></i>Welcome Back</h3>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="alert alert-danger py-2 text-center small">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
        <form method="POST">
            <div class="mb-3">
                <label class="form-label text-muted small">Username</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="mb-4">
                <label class="form-label text-muted small">Password</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Sign In</button>
        </form>
        <p class="text-center mt-4 text-muted small">Don't have an account? <a href="/register" class="text-decoration-none fw-bold" style="color: #4f46e5;">Sign Up</a></p>
    </div>
</body>
</html>
"""

REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Register - Notes App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; height: 100vh; font-family: 'Segoe UI', sans-serif; }
        .auth-card { width: 100%; max-width: 400px; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .btn-primary { background: #4f46e5; border: none; padding: 10px; font-weight: 600; }
        .btn-primary:hover { background: #4338ca; }
        .form-control { padding: 12px; border-radius: 8px; border: 1px solid #e5e7eb; }
    </style>
</head>
<body>
    <div class="auth-card">
        <h3 class="text-center mb-4 fw-bold text-dark"><i class="bi bi-journal-plus me-2"></i>Create Account</h3>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="alert alert-danger py-2 text-center small">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
        <form method="POST">
            <div class="mb-3">
                <label class="form-label text-muted small">Username</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="mb-4">
                <label class="form-label text-muted small">Password</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Sign Up</button>
        </form>
        <p class="text-center mt-4 text-muted small">Already have an account? <a href="/login" class="text-decoration-none fw-bold" style="color: #4f46e5;">Sign In</a></p>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Notes</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        body { background: #f3f4f6; font-family: 'Segoe UI', sans-serif; }
        .navbar { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.03); padding: 1rem 2rem; }
        .navbar-brand { font-weight: 700; color: #4f46e5 !important; font-size: 1.25rem; }
        .sidebar { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.03); height: fit-content; }
        .note-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.03); transition: transform 0.2s; border-left: 4px solid #4f46e5; height: 100%; }
        .note-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .note-card.pinned { border-left-color: #f59e0b; background: #fffbeb; }
        .btn-add { background: #4f46e5; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: 600; width: 100%; }
        .btn-add:hover { background: #4338ca; color: white; }
        .form-control, .form-select { border-radius: 8px; border: 1px solid #e5e7eb; padding: 10px; }
        .badge-cat { background: #e0e7ff; color: #4f46e5; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
        .btn-delete { color: #ef4444; background: #fee2e2; border: none; padding: 5px 10px; border-radius: 6px; font-size: 0.8rem; }
        .btn-delete:hover { background: #fecaca; }
        .btn-pin { color: #f59e0b; background: #fef3c7; border: none; padding: 5px 10px; border-radius: 6px; font-size: 0.8rem; }
        .btn-pin:hover { background: #fde68a; }
        .btn-edit { color: #3b82f6; background: #dbeafe; border: none; padding: 5px 10px; border-radius: 6px; font-size: 0.8rem; }
        .btn-edit:hover { background: #bfdbfe; }
        .stat-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.03); text-align: center; }
        .stat-card h3 { color: #4f46e5; font-size: 2rem; font-weight: 700; margin: 0; }
        .stat-card p { color: #6b7280; margin: 0; font-size: 0.875rem; }
        .search-box { background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.03); margin-bottom: 1.5rem; }
        .category-filter { background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.03); margin-bottom: 1.5rem; }
        .filter-btn { background: #f3f4f6; border: none; padding: 5px 15px; border-radius: 20px; font-size: 0.875rem; margin: 2px; }
        .filter-btn.active { background: #4f46e5; color: white; }
        .filter-btn:hover { background: #e5e7eb; }
        .empty-state { text-align: center; padding: 3rem; color: #9ca3af; }
        .empty-state i { font-size: 4rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="#"><i class="bi bi-journal-richtext me-2"></i>Notes App</a>
            <div class="d-flex align-items-center">
                <span class="me-3 text-muted small">Hi, <strong>{{ current_user.username }}</strong></span>
                <a href="/logout" class="btn btn-outline-secondary btn-sm">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <!-- Statistics Cards -->
        <div class="row g-3 mb-4">
            <div class="col-md-3">
                <div class="stat-card">
                    <h3>{{ total_notes }}</h3>
                    <p>Total Notes</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <h3>{{ pinned_count }}</h3>
                    <p>Pinned Notes</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <h3>{{ categories|length }}</h3>
                    <p>Categories</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <h3>{{ today_notes }}</h3>
                    <p>Added Today</p>
                </div>
            </div>
        </div>

        <div class="row g-4">
            <!-- Sidebar: Add Note -->
            <div class="col-md-4">
                <div class="sidebar">
                    <h5 class="fw-bold mb-3"><i class="bi bi-plus-circle me-2"></i>Add New Note</h5>
                    <form method="POST" action="/add_note">
                        <div class="mb-3">
                            <input type="text" name="title" class="form-control" placeholder="Note Title" required>
                        </div>
                        <div class="mb-3">
                            <select name="category" class="form-select">
                                <option value="General">General</option>
                                <option value="Work">Work</option>
                                <option value="Personal">Personal</option>
                                <option value="Ideas">Ideas</option>
                                <option value="Important">Important</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <textarea name="content" class="form-control" rows="4" placeholder="Write your note..." required></textarea>
                        </div>
                        <div class="mb-3 form-check">
                            <input type="checkbox" name="pinned" class="form-check-input" id="pinned">
                            <label class="form-check-label" for="pinned">Pin this note</label>
                        </div>
                        <button type="submit" class="btn-add">Save Note</button>
                    </form>
                </div>
            </div>

            <!-- Main: Notes Grid -->
            <div class="col-md-8">
                <!-- Search Box -->
                <div class="search-box">
                    <div class="input-group">
                        <span class="input-group-text bg-white border-end-0"><i class="bi bi-search"></i></span>
                        <input type="text" id="searchInput" class="form-control border-start-0" placeholder="Search notes by title or content..." onkeyup="searchNotes()">
                    </div>
                </div>

                <!-- Category Filter -->
                <div class="category-filter">
                    <div class="d-flex flex-wrap gap-2">
                        <button class="filter-btn active" onclick="filterCategory('all')">All</button>
                        {% for cat in categories %}
                        <button class="filter-btn" onclick="filterCategory('{{ cat }}')">{{ cat }}</button>
                        {% endfor %}
                    </div>
                </div>

                <!-- Notes Display -->
                <div id="notesContainer">
                    {% if notes %}
                        <div class="row g-3" id="notesGrid">
                            {% for note in notes %}
                            <div class="col-md-6 note-item" data-category="{{ note.category }}" data-title="{{ note.title.lower() }}" data-content="{{ note.content.lower() }}">
                                <div class="note-card {{ 'pinned' if note.pinned else '' }}">
                                    <div class="d-flex justify-content-between align-items-start mb-2">
                                        <span class="badge-cat">{{ note.category }}</span>
                                        <div>
                                            <form method="POST" action="/toggle_pin/{{ note.id }}" style="display:inline;">
                                                <button type="submit" class="btn-pin" title="{{ 'Unpin' if note.pinned else 'Pin' }}">
                                                    <i class="bi {{ 'bi-pin-fill' if note.pinned else 'bi-pin' }}"></i>
                                                </button>
                                            </form>
                                            <a href="/edit_note/{{ note.id }}" class="btn-edit" title="Edit">
                                                <i class="bi bi-pencil"></i>
                                            </a>
                                            <form method="POST" action="/delete_note/{{ note.id }}" style="display:inline;">
                                                <button type="submit" class="btn-delete" onclick="return confirm('Delete this note?')" title="Delete">
                                                    <i class="bi bi-trash"></i>
                                                </button>
                                            </form>
                                        </div>
                                    </div>
                                    <h6 class="fw-bold mb-2">
                                        {% if note.pinned %}<i class="bi bi-pin-fill text-warning me-1"></i>{% endif %}
                                        {{ note.title }}
                                    </h6>
                                    <p class="text-muted small mb-2" style="line-height: 1.5;">{{ note.content }}</p>
                                    <small class="text-muted" style="font-size: 0.75rem;">
                                        <i class="bi bi-clock"></i> {{ note.created_at.strftime('%Y-%m-%d %H:%M') }}
                                    </small>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <div class="empty-state">
                            <i class="bi bi-journal-x d-block mb-3"></i>
                            <h5>No notes yet</h5>
                            <p>Add your first note using the form on the left!</p>
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <script>
        function searchNotes() {
            const input = document.getElementById('searchInput').value.toLowerCase();
            const notes = document.querySelectorAll('.note-item');
            notes.forEach(note => {
                const title = note.getAttribute('data-title');
                const content = note.getAttribute('data-content');
                note.style.display = (title.includes(input) || content.includes(input)) ? 'block' : 'none';
            });
        }

        function filterCategory(category) {
            const notes = document.querySelectorAll('.note-item');
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            notes.forEach(note => {
                note.style.display = (category === 'all' || note.getAttribute('data-category') === category) ? 'block' : 'none';
            });
        }
    </script>
</body>
</html>
"""

EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Edit Note</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        body { background: #f3f4f6; font-family: 'Segoe UI', sans-serif; padding: 2rem; }
        .edit-card { max-width: 600px; margin: 0 auto; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); }
        .btn-save { background: #4f46e5; color: white; border: none; padding: 10px 30px; border-radius: 8px; font-weight: 600; }
        .btn-save:hover { background: #4338ca; color: white; }
        .btn-cancel { background: #6b7280; color: white; border: none; padding: 10px 30px; border-radius: 8px; font-weight: 600; }
        .btn-cancel:hover { background: #4b5563; color: white; }
    </style>
</head>
<body>
    <div class="edit-card">
        <h3 class="fw-bold mb-4"><i class="bi bi-pencil-square me-2"></i>Edit Note</h3>
        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Title</label>
                <input type="text" name="title" class="form-control" value="{{ note.title }}" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Category</label>
                <select name="category" class="form-select">
                    <option value="General" {{ 'selected' if note.category == 'General' }}>General</option>
                    <option value="Work" {{ 'selected' if note.category == 'Work' }}>Work</option>
                    <option value="Personal" {{ 'selected' if note.category == 'Personal' }}>Personal</option>
                    <option value="Ideas" {{ 'selected' if note.category == 'Ideas' }}>Ideas</option>
                    <option value="Important" {{ 'selected' if note.category == 'Important' }}>Important</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Content</label>
                <textarea name="content" class="form-control" rows="6" required>{{ note.content }}</textarea>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn-save">Save Changes</button>
                <a href="/" class="btn-cancel text-decoration-none">Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>
"""

# --- Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.pinned.desc(), Note.created_at.desc()).all()
    
    total_notes = len(notes)
    pinned_count = sum(1 for note in notes if note.pinned)
    categories = list(set(note.category for note in notes))
    today_notes = sum(1 for note in notes if note.created_at.date() == datetime.utcnow().date())
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                  notes=notes, 
                                  total_notes=total_notes,
                                  pinned_count=pinned_count,
                                  categories=categories,
                                  today_notes=today_notes)

@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    title = request.form['title']
    content = request.form['content']
    category = request.form['category']
    pinned = 'pinned' in request.form
    
    new_note = Note(title=title, content=content, category=category, pinned=pinned, user_id=current_user.id)
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        note.category = request.form['category']
        note.updated_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template_string(EDIT_TEMPLATE, note=note)

@app.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/toggle_pin/<int:note_id>', methods=['POST'])
@login_required
def toggle_pin(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id == current_user.id:
        note.pinned = not note.pinned
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)