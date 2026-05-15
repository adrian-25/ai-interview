# Quick Reference Card

## 🚀 Start Server

```bash
# Quick start (validates everything)
python setup.py && python main.py

# Or use scripts
./run.sh        # Mac/Linux
run.bat         # Windows

# Or direct
uvicorn main:app --reload
```

---

## 🔧 Common Commands

### Setup
```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
```

### Validation
```bash
python setup.py
```

### Testing
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

---

## 📝 Environment Variables

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname
JWT_SECRET=min-32-chars-random-string
OPENAI_API_KEY=sk-your-key-here
CORS_ORIGINS=http://localhost:5173
```

---

## 🧪 Quick Test Flow

```bash
# 1. Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'

# Save the token from response!

# 2. Start session
curl -X POST http://localhost:8000/api/sessions/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"role":"Frontend Developer"}'

# Save the session_id from response!

# 3. Submit answer
curl -X POST http://localhost:8000/api/sessions/SESSION_ID/answer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"answer":"Your answer here"}'

# 4. View dashboard
curl http://localhost:8000/api/dashboard/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 Documentation Files

- `README.md` - Setup guide
- `TESTING_GUIDE.md` - Complete testing instructions
- `DEPLOYMENT.md` - Production deployment
- `BACKEND_READY.md` - Implementation summary
- `QUICK_REFERENCE.md` - This file

---

## 🔗 Useful URLs

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

---

## 🐛 Troubleshooting

### Server won't start
```bash
python setup.py  # Check what's missing
```

### MongoDB connection failed
- Check connection string format
- Verify IP whitelist (0.0.0.0/0)
- Confirm database user credentials

### OpenAI API errors
- Verify API key is valid
- Check account has credits

### 401 Unauthorized
- Token expired (24 hours)
- Token format: `Bearer TOKEN`
- Token not in Authorization header

---

## 📦 Project Structure

```
backend/
├── main.py              # Entry point
├── config.py            # Settings
├── database.py          # MongoDB
├── models/              # Data models
├── services/            # Business logic
├── routers/             # API endpoints
└── utils/               # Helpers
```

---

## ✅ Success Indicators

- [ ] `python setup.py` passes
- [ ] Server starts without errors
- [ ] `/health` returns 200
- [ ] `/docs` loads Swagger UI
- [ ] Can create account
- [ ] Can login
- [ ] Can start session
- [ ] AI generates question
- [ ] Can submit answer
- [ ] Dashboard shows data

---

## 🎯 Next Steps

1. ✅ Backend complete
2. ⏳ Build frontend
3. ⏳ Connect frontend to backend
4. ⏳ Deploy both
