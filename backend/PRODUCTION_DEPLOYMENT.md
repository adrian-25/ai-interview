# 🚀 Production Deployment Guide

## Status: Backend Tested Locally ✅

All MVP features working locally. Ready for production deployment.

---

## 📋 Pre-Deployment Checklist

- [x] All local tests passed
- [x] MongoDB Atlas cluster created
- [x] OpenAI API key obtained
- [x] JWT secret generated
- [x] No secrets in code
- [x] Environment variables configured
- [x] CORS configured
- [x] Health endpoint working
- [x] Logging enabled

---

## 🎯 Deployment Option 1: Render (Recommended)

### Why Render?
- ✅ Free tier available
- ✅ Auto-deploys from GitHub
- ✅ Easy environment variable management
- ✅ Built-in SSL
- ✅ No cold starts on paid tier

### Step 1: Prepare GitHub Repository

```bash
# Ensure code is pushed to GitHub
cd backend
git add .
git commit -m "Backend ready for deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:

**Basic Settings:**
- **Name**: `ai-interview-coach-api`
- **Region**: Choose closest to your users (e.g., Oregon USA)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- **Free** (for testing) - Note: Spins down after 15 min inactivity
- **Starter** ($7/month) - Recommended for production, no cold starts

### Step 4: Set Environment Variables

In Render dashboard, go to "Environment" tab and add:

```
MONGODB_URI=mongodb+srv://YOUR_USER:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/ai-interview-coach?retryWrites=true&w=majority
JWT_SECRET=your-super-secret-key-min-32-chars-long-change-this
OPENAI_API_KEY=sk-your-openai-api-key-here
CORS_ORIGINS=*
APP_ENV=production
```

**Important Notes:**
- Use your actual MongoDB Atlas connection string
- Generate a strong JWT secret (32+ characters)
- Use your OpenAI API key
- `CORS_ORIGINS=*` allows all origins (change after frontend deployed)

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start the server
3. Wait 5-10 minutes for first deployment

### Step 6: Get Your API URL

Your API will be available at:
```
https://ai-interview-coach-api.onrender.com
```

Save this URL - you'll need it for frontend integration!

---

## 🎯 Deployment Option 2: Railway

### Why Railway?
- ✅ Simple deployment
- ✅ $5 free credit per month
- ✅ Fast deployments
- ✅ Good developer experience

### Step 1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub

### Step 2: Create New Project

1. Click "New Project"
2. Choose "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python

### Step 3: Configure

1. Go to project settings
2. **Root Directory**: Set to `backend`
3. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Python Version**: 3.11

### Step 4: Set Environment Variables

In Railway dashboard, add variables:

```
MONGODB_URI=mongodb+srv://YOUR_USER:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/ai-interview-coach
JWT_SECRET=your-super-secret-key-min-32-chars
OPENAI_API_KEY=sk-your-openai-api-key
CORS_ORIGINS=*
APP_ENV=production
```

### Step 5: Deploy

Railway automatically deploys on push to main branch.

### Step 6: Get Your API URL

Find your URL in Railway dashboard (e.g., `https://your-app.up.railway.app`)

---

## 🧪 Production Testing

Once deployed, test the live API:

### Test 1: Health Check

```bash
curl https://YOUR_DEPLOYED_URL/health
```

**Expected:**
```json
{"status":"healthy"}
```

### Test 2: API Documentation

Open browser:
```
https://YOUR_DEPLOYED_URL/docs
```

Should show Swagger UI.

### Test 3: Create Account

```bash
curl -X POST https://YOUR_DEPLOYED_URL/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"prod-test@example.com","password":"Test1234"}'
```

**Expected:**
```json
{
  "success": true,
  "data": {
    "user_id": "...",
    "email": "prod-test@example.com",
    "token": "eyJ..."
  },
  "message": "Account created successfully"
}
```

**Save the token!**

### Test 4: Start Interview Session

```bash
curl -X POST https://YOUR_DEPLOYED_URL/api/sessions/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"role":"Frontend Developer"}'
```

**Expected:**
```json
{
  "session_id": "...",
  "first_question": "Can you explain..."
}
```

**Save the session_id!**

### Test 5: Submit Answer

```bash
curl -X POST https://YOUR_DEPLOYED_URL/api/sessions/SESSION_ID/answer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"answer":"This is my answer to the interview question"}'
```

**Expected:**
```json
{
  "evaluation": {
    "score": 7.5,
    "strengths": ["...", "..."],
    "improvements": ["...", "..."],
    "suggestion": "..."
  },
  "next_question": "..."
}
```

### Test 6: End Session

```bash
curl -X POST https://YOUR_DEPLOYED_URL/api/sessions/SESSION_ID/end \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 7: Get Dashboard

```bash
curl https://YOUR_DEPLOYED_URL/api/dashboard/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Production Validation Checklist

- [ ] Health endpoint returns 200
- [ ] API docs load at /docs
- [ ] Can create account
- [ ] Can login
- [ ] JWT authentication works
- [ ] Can start interview session
- [ ] OpenAI generates questions
- [ ] Can submit answers
- [ ] OpenAI evaluates answers
- [ ] Sessions saved to MongoDB
- [ ] Dashboard returns data
- [ ] No CORS errors
- [ ] No 500 errors
- [ ] Proper error messages for invalid input
- [ ] 401 for missing/invalid token
- [ ] All 5 roles work

---

## 🔒 Security Verification

### Check 1: No Secrets Exposed

```bash
curl https://YOUR_DEPLOYED_URL/
```

Response should NOT contain:
- MongoDB connection strings
- API keys
- JWT secrets

### Check 2: Error Handling

```bash
# Invalid credentials
curl -X POST https://YOUR_DEPLOYED_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"fake@example.com","password":"wrong"}'
```

Should return 401, NOT stack trace.

### Check 3: Authorization

```bash
# No token
curl -X POST https://YOUR_DEPLOYED_URL/api/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"role":"Frontend Developer"}'
```

Should return 401 or 422, NOT 500.

---

## 🐛 Troubleshooting

### Deployment Fails

**Check Render/Railway logs for:**
- Missing dependencies
- Python version mismatch
- Environment variable errors

**Fix:**
- Verify `requirements.txt` is correct
- Check `runtime.txt` specifies Python 3.11
- Ensure all env vars are set

### MongoDB Connection Fails

**Symptoms:**
- 500 errors on all endpoints
- "Failed to connect to MongoDB" in logs

**Fix:**
1. Verify connection string format
2. Check MongoDB Atlas IP whitelist includes `0.0.0.0/0`
3. Confirm database user credentials
4. Test connection string locally first

### OpenAI API Errors

**Symptoms:**
- Sessions start but questions fail
- "OpenAI API error" in logs

**Fix:**
1. Verify API key is valid
2. Check OpenAI account has credits
3. Monitor rate limits in OpenAI dashboard

### CORS Errors

**Symptoms:**
- Frontend can't connect
- "CORS policy" errors in browser console

**Fix:**
1. Add frontend domain to `CORS_ORIGINS`
2. Format: `https://your-frontend.vercel.app`
3. Multiple origins: `https://domain1.com,https://domain2.com`
4. For testing: Use `*` (not recommended for production)

### Cold Starts (Render Free Tier)

**Symptoms:**
- First request after 15 min takes 30+ seconds
- Subsequent requests fast

**Fix:**
- Upgrade to Render Starter plan ($7/month)
- Or accept cold starts for free tier

---

## 📊 Monitoring

### Render

**View Logs:**
1. Go to your service dashboard
2. Click "Logs" tab
3. Monitor for errors

**Set Up Alerts:**
1. Go to "Settings"
2. Add email for deployment notifications
3. Enable health check alerts

### Railway

**View Logs:**
```bash
railway logs
```

Or view in dashboard.

**Monitor Metrics:**
- CPU usage
- Memory usage
- Request count

---

## 🔄 Update Deployment

### Render

Automatically deploys on push to main:

```bash
git add .
git commit -m "Update backend"
git push origin main
```

Render detects changes and redeploys.

### Railway

Same - auto-deploys on push to main.

### Manual Redeploy

**Render:** Click "Manual Deploy" → "Deploy latest commit"

**Railway:** Click "Deploy" in dashboard

---

## 🎯 Post-Deployment Configuration

### Update CORS for Frontend

Once frontend is deployed, update `CORS_ORIGINS`:

```
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

**Never use `*` in production with credentials!**

### Set Up Custom Domain (Optional)

**Render:**
1. Go to "Settings" → "Custom Domain"
2. Add your domain
3. Update DNS records

**Railway:**
1. Go to "Settings" → "Domains"
2. Add custom domain
3. Update DNS

---

## 📈 Performance Optimization

### Database Indexes

Already configured in `database.py`:
- users.email (unique)
- sessions.user_id
- sessions.status
- sessions.started_at

### Connection Pooling

Already configured:
- Max pool size: 10
- Min pool size: 1

### API Response Time

**Target:**
- Health check: < 100ms
- Auth endpoints: < 500ms
- Session start: < 3s (includes OpenAI call)
- Submit answer: < 5s (includes OpenAI evaluation)

---

## 💰 Cost Estimation

### Free Tier

**Render Free:**
- ✅ Free forever
- ❌ Spins down after 15 min inactivity
- ❌ 750 hours/month limit

**Railway Free:**
- ✅ $5 credit/month
- ✅ No cold starts
- ❌ Limited to credit amount

**MongoDB Atlas M0:**
- ✅ Free forever
- ✅ 512 MB storage
- ✅ Shared CPU

**OpenAI:**
- Pay per use
- GPT-3.5-turbo: ~$0.002 per request
- Estimate: $5-10/month for moderate use

### Paid Tier (Recommended for Production)

**Render Starter:** $7/month
- No cold starts
- Better performance
- 24/7 uptime

**MongoDB Atlas M10:** ~$57/month
- Dedicated resources
- Automated backups
- Better performance

**Total:** ~$70-80/month for production-ready setup

---

## ✅ Deployment Success Criteria

Backend is production-ready when:

- [ ] Deployed to Render or Railway
- [ ] All environment variables configured
- [ ] Health endpoint returns 200
- [ ] API documentation accessible
- [ ] Can create account in production
- [ ] Can login in production
- [ ] Can start interview session
- [ ] OpenAI generates questions
- [ ] Can submit answers
- [ ] OpenAI evaluates answers
- [ ] Sessions persist to MongoDB
- [ ] Dashboard returns data
- [ ] No CORS errors
- [ ] No 500 errors
- [ ] Proper error handling
- [ ] Logs show no errors
- [ ] All 5 roles tested

---

## 🎉 Next Steps

Once deployment is confirmed stable:

1. ✅ Backend deployed and tested
2. ✅ Production URL obtained
3. ⏳ Build frontend
4. ⏳ Configure frontend with production API URL
5. ⏳ Deploy frontend to Vercel
6. ⏳ Update CORS to frontend domain
7. ⏳ Test end-to-end flow

---

## 📞 Support Resources

**Render:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

**MongoDB Atlas:**
- Docs: https://docs.atlas.mongodb.com
- Support: https://support.mongodb.com

**OpenAI:**
- Docs: https://platform.openai.com/docs
- Status: https://status.openai.com
