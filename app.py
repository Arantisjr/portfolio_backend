import os
import re
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone  # Added timezone import
from dotenv import load_dotenv

# Loading the environment variables
load_dotenv()

app = Flask(__name__)

# Configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

db = SQLAlchemy(app)

# Utility functions
def generate_slug(title):
    return re.sub(r'[^a-zA-Z0-9]+', '-', title.lower())

def estimate_reading_time(text):
    words = len(text.split())
    return max(1, words // 200)  # 200 words per minute

class Writing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    subtitle = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False, default='Me')  # Fixed missing comma
    reading_time = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc)  # Timezone-aware
    )
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)  # Auto-updates
    )
    
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'subtitle': self.subtitle,
            'content': self.content,
            'author': self.author,
            'reading_time': self.reading_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Routes
@app.route('/writings', methods=['GET'])
def get_writings():
    writings = Writing.query.order_by(Writing.created_at.desc()).all()  # Removed extra )
    return jsonify([w.serialize() for w in writings])  # Added () to serialize

@app.route('/writings/<slug>', methods=['GET'])
def get_writing_by_slug(slug):
    writing = Writing.query.filter_by(slug=slug).first_or_404()
    return jsonify(writing.serialize())  # Added () to serialize

@app.route('/writings', methods=['POST'])
def add_writing():
    token = request.headers.get('Authorization')
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    subtitle = data.get('subtitle')
    author = data.get('author', 'Me')
    
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    
    slug = generate_slug(title)
    reading_time = estimate_reading_time(content)
    
    new_writing = Writing(
        title=title,
        slug=slug,
        subtitle=subtitle,
        content=content,
        author=author,
        reading_time=reading_time
    )
    db.session.add(new_writing)
    db.session.commit()
    return jsonify(new_writing.serialize()), 201

@app.route('/writings/<int:writing_id>', methods=['PUT'])
def update_writing(writing_id):
    token = request.headers.get('Authorization')
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    writing = Writing.query.get_or_404(writing_id)
    
    if 'title' in data:
        writing.title = data['title']
        writing.slug = generate_slug(data['title'])
    if 'content' in data:
        writing.content = data['content']
        writing.reading_time = estimate_reading_time(data['content'])
    if 'subtitle' in data:
        writing.subtitle = data['subtitle']
    if 'author' in data:
        writing.author = data['author']
    
    db.session.commit()
    return jsonify(writing.serialize())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv('FLASK_ENV') == 'development')