# Smartcal Backend

A FastAPI backend for a calendar booking application with user management, JWT authentication, availability, agenda, team meetings, and calendar sync support.

## Features
- User registration, login, JWT auth
- Password reset via email
- Weekly availability slots
- Calendar and agenda management
- Team meetings (with internal/external detection)
- Google/Outlook OAuth2 fields for calendar sync
- Rate limiting (default: 5 req/sec per IP)
- Request and error logging middleware
- Swagger API docs at `/docs`

## Setup

### 1. Clone the repo
```
git clone <repo-url>
cd Smartcal-backend
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Create `.env` file
```
SECRET_KEY=your-secret-key
RATE_LIMIT=5
```

### 4. Initialize the database
```
python -m app.db_init
```

### 5. Run a dummy SMTP server (for email testing)
```
python -m smtpd -c DebuggingServer -n localhost:1025
```

### 6. Start the FastAPI server
```
uvicorn main:app --reload
```

## API Documentation
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Configuration
- All secrets and config are loaded from `.env`.
- Change `RATE_LIMIT` in `.env` to adjust rate limiting.

## Dependencies
- fastapi
- uvicorn
- sqlalchemy
- passlib[bcrypt]
- python-jose
- pydantic
- pytz
- python-dotenv

## License
MIT 