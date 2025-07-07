# Flask Writings API

A simple Flask REST API for managing writings/articles with CRUD operations and authentication.

## Quick Start

1. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-cors python-dotenv
   ```

2. **Create `.env` file**
   ```env
   DATABASE_URL=sqlite:///writings.db
   SECRET_KEY=your-secret-key
   AUTH_TOKEN=your-auth-token
   FLASK_ENV=development
   ```

3. **Run**
   ```bash
   python app.py
   ```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/writings` | Get all writings | No |
| `GET` | `/writings/<slug>` | Get writing by slug | No |
| `POST` | `/writings` | Create new writing | Yes |
| `PUT` | `/writings/<id>` | Update writing | Yes |
| `DELETE` | `/writings/<id>` | Delete writing | Yes |

## Authentication
For protected routes, include header:
```
Authorization: Bearer <your-auth-token>
```

## Example Request
```bash
curl -X POST http://localhost:5000/writings \
  -H "Authorization: Bearer your-auth-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Why programming?",
    "subtitle": "The art of turning ideas into digital reality",
    "content": "Programming is more than just writing code...",
    "author": "@AranTech"
  }'
```

## Features
- Auto-generated slugs from titles
- Reading time estimation (200 words/minute)
- CORS enabled
- SQLAlchemy ORM with automatic timestamps