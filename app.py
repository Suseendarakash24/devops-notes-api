from flask import Flask, jsonify, request
import os

app = Flask(__name__)

notes = []

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>DevOps Notes API</title>
        <style>
            body { 
                font-family: Arial; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                min-height: 100vh;
            }
            .box {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 { color: #667eea; text-align: center; }
            .status { 
                background: #28a745; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
                text-align: center;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🚀 DevOps Notes API</h1>
            <div class="status">✅ API is Live & Running!</div>
            <h3>Welcome to my DevOps project!</h3>
            <p>This API is deployed using:</p>
            <ul>
                <li>✅ Docker Containerization</li>
                <li>✅ GitHub Actions CI/CD</li>
                <li>✅ Auto-deployment to Render</li>
            </ul>
            <hr>
            <p><strong>Try these endpoints:</strong></p>
            <ul>
                <li><a href="/health">/health</a> - Health Check</li>
                <li><a href="/notes">/notes</a> - Get all notes (JSON)</li>
            </ul>
        </div>
    </body>
    </html>
    """

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)