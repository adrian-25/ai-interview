# 🚀 START HERE - AI Interview Coach Backend

## ⚡ Quick Start (5 Minutes)

### 1. Prerequisites

- Python 3.11 or higher
- MongoDB Atlas account (free tier)
- OpenAI API key

### 2. Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### 3. Edit `.env` File

Open `backend/.env` and add your credentials:

```env
MONGODB_URI=mongodb+srv://YOUR_USER:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/ai-interview-coach
JWT_SECRET=generate-a-random-32-character-string-here
OPENAI_API_KEY=sk-your-openai-api-key-here
CORS_ORIGINS=http://localhost:5173
```

**Need help getting these?**
- MongoDB: https://cloud.mongodb.com (free M0 cluster)
- OpenAI: https://platform.openai.com/api-keys
- JWT Secret: Run `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 4. Validate Setup

```bash
python setup.py
```

If all checks pass ✅, you're ready!

### 5. Start Server

```bash
python main.py
```

Server starts at: `http://localhost:8000`

### 6. Test It Works

Open browser: `http://localhost:8000/docs`

You should see the Swagger API documentation!

---

## 🧪 Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Create account
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
```

If you get a success response with a token, **it's working!** 🎉

---

## 📚 What to Read Next

1. **Testing the API**: `backend/TESTING_GUIDE.md`
   - Complete curl commands for all endpoints
   - Test the full interview flow
   - Verify all features work

2. **Deployment**: `backend/DEPLOYMENT.md`
   - Deploy to Render/Railway
   - Production configuration
   - MongoDB Atlas setup

3. **Development**: `backend/README.md`
   - Project structure
   - Code organization
   - Development workflow

---

## 🎯 Your Options Now

### Option A: Test Backend Thoroughly
Follow `backend/TESTING_GUIDE.md` to test all endpoints

### Option B: Deploy Backend
Follow `backend/DEPLOYMENT.md` to deploy to production

### Option C: Build Frontend
Backend is ready - start building React frontend

---

## ❓ Troubleshooting

### Server won't start?
```bash
python setup.py  # Shows what's wrong
```

### MongoDB connection failed?
- Check connection string format
- Verify IP whitelist (0.0.0.0/0 for dev)
- Confirm database user credentials

### OpenAI API errors?
- Verify API key is valid
- Check account has credits

---

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] MongoDB Atlas cluster created
- [ ] OpenAI API key obtained
- [ ] `python setup.py` passes
- [ ] Server starts without errors
- [ ] `/health` returns 200
- [ ] `/docs` loads Swagger UI
- [ ] Can create account via curl

---

## 🎉 You're Ready!

Backend is fully implemented and ready for:
- ✅ Local development
- ✅ API testing
- ✅ Frontend integration
- ✅ Production deployment

**Happy coding! 🚀**
