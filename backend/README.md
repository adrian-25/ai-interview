# AI Interview Coach - Backend

FastAPI backend for the AI Interview Coach application.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `MONGODB_URI`: Your MongoDB Atlas connection string
- `JWT_SECRET`: Secret key for JWT tokens (generate a random string)
- `OPENAI_API_KEY`: Your OpenAI API key
- `CORS_ORIGINS`: Comma-separated list of allowed origins

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Or using Python
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/verify` - Verify JWT token

### Sessions
- `POST /api/sessions/start` - Start new interview session
- `POST /api/sessions/{id}/answer` - Submit answer and get evaluation
- `POST /api/sessions/{id}/end` - End interview session
- `GET /api/sessions/{id}` - Get session details
- `GET /api/sessions/resume/current` - Resume in-progress session

### Dashboard
- `GET /api/dashboard/sessions` - Get user's sessions (paginated)
- `GET /api/dashboard/analytics` - Get user's analytics

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── database.py            # MongoDB connection
├── models/                # Pydantic models
│   ├── user.py
│   └── session.py
├── services/              # Business logic
│   ├── auth_service.py
│   ├── ai_service.py
│   └── session_service.py
└── routers/               # API endpoints
    ├── auth.py
    ├── sessions.py
    ├── dashboard.py
    └── dependencies.py
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Linting

```bash
pylint **/*.py
```

## Deployment

### Environment Variables for Production

Make sure to set secure values for:
- `JWT_SECRET` - Use a strong random string
- `MONGODB_URI` - Use MongoDB Atlas production cluster
- `CORS_ORIGINS` - Set to your frontend domain only

### Deploy to Render/Railway

1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## MongoDB Atlas Setup

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free M0 cluster
3. Create database user with read/write permissions
4. Whitelist IP addresses (0.0.0.0/0 for development)
5. Get connection string and add to `.env`

## Troubleshooting

### MongoDB Connection Issues
- Verify connection string format
- Check IP whitelist in MongoDB Atlas
- Ensure database user has correct permissions

### OpenAI API Issues
- Verify API key is valid
- Check API usage limits
- Ensure sufficient credits

### CORS Issues
- Add frontend URL to `CORS_ORIGINS` in `.env`
- Restart server after changing environment variables
