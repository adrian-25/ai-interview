# Backend Testing Guide

Complete guide to manually test the AI Interview Coach backend API.

## Prerequisites

1. **MongoDB Atlas Setup**
   - Create free cluster at https://cloud.mongodb.com
   - Create database user
   - Whitelist IP: 0.0.0.0/0 (for development)
   - Get connection string

2. **OpenAI API Key**
   - Get from https://platform.openai.com/api-keys
   - Ensure you have credits

3. **Environment Setup**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your values
   ```

4. **Install & Run**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python main.py
   ```

Server should start at: `http://localhost:8000`

---

## Test Flow

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. Create Account (Signup)

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"Test1234\"}"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "65abc123...",
    "email": "test@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Account created successfully"
}
```

**Save the token** - you'll need it for authenticated requests!

**Test Cases:**
- ❌ Weak password (< 8 chars): Should return 400
- ❌ No uppercase: Should return 400
- ❌ No number: Should return 400
- ❌ Invalid email: Should return 400
- ❌ Duplicate email: Should return 400

---

### 3. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"Test1234\"}"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "65abc123...",
    "email": "test@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Login successful"
}
```

**Test Cases:**
- ❌ Wrong password: Should return 401
- ❌ Non-existent email: Should return 401

---

### 4. Verify Token

```bash
curl "http://localhost:8000/api/auth/verify?token=YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user_id": "65abc123..."
  }
}
```

---

### 5. Start Interview Session

**Replace `YOUR_TOKEN` with the token from signup/login**

```bash
curl -X POST http://localhost:8000/api/sessions/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "{\"role\":\"Frontend Developer\"}"
```

**Available Roles:**
- `Frontend Developer`
- `Backend Developer`
- `Full Stack Developer`
- `AI/ML Engineer`
- `Data Analyst`

**Expected Response:**
```json
{
  "session_id": "65def456...",
  "first_question": "Can you explain the difference between let, const, and var in JavaScript?"
}
```

**Save the session_id** - you'll need it for submitting answers!

**Test Cases:**
- ❌ No token: Should return 401
- ❌ Invalid token: Should return 401
- ❌ Invalid role: Should return 422

---

### 6. Submit Answer

```bash
curl -X POST http://localhost:8000/api/sessions/SESSION_ID/answer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "{\"answer\":\"let and const are block-scoped while var is function-scoped. const cannot be reassigned while let can. var has hoisting behavior that can lead to bugs.\"}"
```

**Expected Response:**
```json
{
  "evaluation": {
    "score": 8.5,
    "strengths": [
      "Correctly identified block vs function scoping",
      "Mentioned const immutability",
      "Noted hoisting issues with var"
    ],
    "improvements": [
      "Could mention temporal dead zone",
      "Could provide code examples"
    ],
    "suggestion": "A complete answer would include: let and const are block-scoped..."
  },
  "next_question": "What is the virtual DOM and how does React use it?"
}
```

**Test Cases:**
- ❌ Empty answer: Should return 422
- ❌ Answer > 2000 chars: Should return 422
- ❌ Wrong session_id: Should return 404
- ❌ Session owned by different user: Should return 404

---

### 7. Submit Another Answer

Repeat step 6 with the new question. You can submit multiple answers in a session.

---

### 8. End Session

```bash
curl -X POST http://localhost:8000/api/sessions/SESSION_ID/end \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "session_id": "65def456...",
  "status": "completed"
}
```

---

### 9. Get Session Details

```bash
curl http://localhost:8000/api/sessions/SESSION_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "session_id": "65def456...",
  "role": "Frontend Developer",
  "status": "completed",
  "started_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:45:00",
  "conversation": [
    {
      "type": "question",
      "content": "Can you explain...",
      "timestamp": "2024-01-15T10:30:00",
      "evaluation": null
    },
    {
      "type": "answer",
      "content": "let and const are...",
      "timestamp": "2024-01-15T10:32:00",
      "evaluation": null
    },
    {
      "type": "evaluation",
      "content": "",
      "timestamp": "2024-01-15T10:32:05",
      "evaluation": {
        "score": 8.5,
        "strengths": [...],
        "improvements": [...],
        "suggestion": "..."
      }
    }
  ],
  "average_score": 8.5
}
```

---

### 10. Get All Sessions (Dashboard)

```bash
curl "http://localhost:8000/api/dashboard/sessions?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "sessions": [
    {
      "id": "65def456...",
      "role": "Frontend Developer",
      "status": "completed",
      "started_at": "2024-01-15T10:30:00",
      "completed_at": "2024-01-15T10:45:00",
      "average_score": 8.5,
      "question_count": 3
    }
  ],
  "total": 1
}
```

---

### 11. Get Analytics

```bash
curl http://localhost:8000/api/dashboard/analytics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "total_questions": 3,
  "average_score": 8.5,
  "total_sessions": 1,
  "completed_sessions": 1
}
```

---

### 12. Resume In-Progress Session

```bash
curl http://localhost:8000/api/sessions/resume/current \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
- If session exists: Full session object
- If no in-progress session: 404 error

---

## Complete Test Sequence

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Signup
TOKEN=$(curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}' \
  | jq -r '.data.token')

echo "Token: $TOKEN"

# 3. Start session
SESSION=$(curl -X POST http://localhost:8000/api/sessions/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"role":"Frontend Developer"}' \
  | jq -r '.session_id')

echo "Session ID: $SESSION"

# 4. Submit answer
curl -X POST http://localhost:8000/api/sessions/$SESSION/answer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"answer":"This is my answer to the question"}' \
  | jq

# 5. End session
curl -X POST http://localhost:8000/api/sessions/$SESSION/end \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# 6. Get dashboard
curl http://localhost:8000/api/dashboard/sessions \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

---

## Troubleshooting

### MongoDB Connection Failed
- Check connection string format
- Verify IP whitelist (0.0.0.0/0 for dev)
- Confirm database user credentials

### OpenAI API Errors
- Verify API key is valid
- Check account has credits
- Look for rate limit errors in logs

### 401 Unauthorized
- Token expired (24 hours)
- Token format incorrect (must be `Bearer TOKEN`)
- Token not included in header

### 422 Validation Error
- Check request body matches expected format
- Verify all required fields present
- Check field types (string, number, etc.)

---

## Success Checklist

- [ ] Health endpoint returns 200
- [ ] Can create account with valid credentials
- [ ] Cannot create account with weak password
- [ ] Cannot create duplicate account
- [ ] Can login with correct credentials
- [ ] Cannot login with wrong password
- [ ] Token verification works
- [ ] Can start interview session
- [ ] AI generates first question
- [ ] Can submit answer
- [ ] AI evaluates answer with score 0-10
- [ ] AI generates next question
- [ ] Can end session
- [ ] Average score calculated correctly
- [ ] Can view session details
- [ ] Can view all sessions
- [ ] Analytics show correct stats
- [ ] Only session owner can access session

---

## Next Steps

Once all tests pass:
1. ✅ Backend is ready
2. ✅ Can proceed to frontend development
3. ✅ Frontend can integrate with these endpoints
