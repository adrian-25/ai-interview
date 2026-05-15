# Backend Deployment Guide

Guide for deploying the AI Interview Coach backend to production.

## Pre-Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created with read/write permissions
- [ ] IP whitelist configured (0.0.0.0/0 or specific IPs)
- [ ] OpenAI API key obtained
- [ ] Strong JWT secret generated
- [ ] All tests passing locally

---

## MongoDB Atlas Setup

### 1. Create Cluster

1. Go to https://cloud.mongodb.com
2. Sign up / Log in
3. Click "Build a Database"
4. Choose "M0 Free" tier
5. Select cloud provider and region (closest to your users)
6. Name your cluster (e.g., "ai-interview-coach")
7. Click "Create"

### 2. Create Database User

1. Go to "Database Access" in left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Username: `aicoach` (or your choice)
5. Generate secure password (save it!)
6. Database User Privileges: "Read and write to any database"
7. Click "Add User"

### 3. Configure Network Access

1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. For development: Click "Allow Access from Anywhere" (0.0.0.0/0)
4. For production: Add specific IP addresses of your deployment platform
5. Click "Confirm"

### 4. Get Connection String

1. Go to "Database" in left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your database user password
6. Replace `<dbname>` with `ai-interview-coach` (or your choice)

Example:
```
mongodb+srv://aicoach:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/ai-interview-coach?retryWrites=true&w=majority
```

---

## Deployment Options

### Option 1: Render (Recommended)

#### Step 1: Prepare Repository

1. Push code to GitHub
2. Ensure `requirements.txt` is in backend directory

#### Step 2: Create Web Service

1. Go to https://render.com
2. Sign up / Log in
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `ai-interview-coach-api`
   - **Region**: Choose closest to users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (for testing) or Starter ($7/month)

#### Step 3: Set Environment Variables

In Render dashboard, go to "Environment" tab and add:

```
MONGODB_URI=mongodb+srv://aicoach:PASSWORD@cluster0.xxxxx.mongodb.net/ai-interview-coach
JWT_SECRET=your-super-secret-key-min-32-chars-long
OPENAI_API_KEY=sk-your-openai-api-key
CORS_ORIGINS=https://your-frontend-domain.vercel.app
APP_ENV=production
```

#### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your API will be at: `https://ai-interview-coach-api.onrender.com`

#### Step 5: Test

```bash
curl https://ai-interview-coach-api.onrender.com/health
```

---

### Option 2: Railway

#### Step 1: Install Railway CLI (Optional)

```bash
npm install -g @railway/cli
railway login
```

#### Step 2: Deploy via Dashboard

1. Go to https://railway.app
2. Sign up / Log in
3. Click "New Project"
4. Choose "Deploy from GitHub repo"
5. Select your repository
6. Railway auto-detects Python

#### Step 3: Configure

1. Go to project settings
2. Set Root Directory: `backend`
3. Add environment variables (same as Render above)
4. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Step 4: Deploy

Railway automatically deploys on push to main branch.

---

### Option 3: Heroku

#### Step 1: Create Procfile

Create `backend/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Step 2: Deploy

```bash
cd backend
heroku login
heroku create ai-interview-coach-api
heroku config:set MONGODB_URI="your-connection-string"
heroku config:set JWT_SECRET="your-secret"
heroku config:set OPENAI_API_KEY="your-key"
heroku config:set CORS_ORIGINS="https://your-frontend.vercel.app"
git push heroku main
```

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/dbname` |
| `JWT_SECRET` | Secret key for JWT tokens (min 32 chars) | `your-super-secret-key-change-in-production` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION_HOURS` | Token expiration time | `24` |
| `APP_ENV` | Environment name | `development` |

---

## Security Best Practices

### 1. JWT Secret

Generate a strong random secret:

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

### 2. CORS Configuration

Set `CORS_ORIGINS` to your exact frontend domain:

```
CORS_ORIGINS=https://your-app.vercel.app
```

Never use `*` in production!

### 3. MongoDB Security

- Use strong database user password
- Restrict IP access to deployment platform IPs
- Enable MongoDB Atlas encryption at rest
- Regularly rotate credentials

### 4. OpenAI API Key

- Never commit API keys to git
- Use environment variables only
- Monitor usage in OpenAI dashboard
- Set usage limits to prevent unexpected charges

---

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://your-api-domain.com/health
```

Expected: `{"status":"healthy"}`

### 2. API Documentation

Visit: `https://your-api-domain.com/docs`

Should show Swagger UI with all endpoints.

### 3. Test Authentication

```bash
curl -X POST https://your-api-domain.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
```

Should return success with token.

### 4. Test AI Integration

Create account → Start session → Verify AI generates question

---

## Monitoring

### Render

- View logs in dashboard
- Set up health check alerts
- Monitor resource usage

### Railway

- View logs with `railway logs`
- Monitor metrics in dashboard
- Set up Sentry for error tracking

### Recommended Tools

- **Logging**: Render/Railway built-in logs
- **Error Tracking**: Sentry (free tier available)
- **Uptime Monitoring**: UptimeRobot (free)
- **Performance**: New Relic (free tier)

---

## Troubleshooting

### Deployment Fails

- Check build logs for errors
- Verify `requirements.txt` is correct
- Ensure Python version is 3.11+

### MongoDB Connection Fails

- Verify connection string format
- Check IP whitelist includes deployment platform
- Confirm database user credentials

### CORS Errors

- Add frontend domain to `CORS_ORIGINS`
- Include protocol (https://)
- No trailing slash

### OpenAI API Errors

- Verify API key is valid
- Check account has credits
- Monitor rate limits

---

## Scaling Considerations

### Free Tier Limitations

- **Render Free**: Spins down after 15 min inactivity (cold starts)
- **Railway Free**: $5 credit/month
- **MongoDB Atlas M0**: 512 MB storage, shared CPU

### When to Upgrade

- Consistent traffic (avoid cold starts)
- More than 100 users
- Need faster response times
- Require more storage

### Upgrade Path

1. **Render**: Starter plan ($7/month) - no cold starts
2. **MongoDB**: M10 cluster ($0.08/hour) - dedicated resources
3. **OpenAI**: Set usage limits, monitor costs

---

## Backup Strategy

### MongoDB Backups

- Atlas M0: No automated backups
- Atlas M10+: Automated daily backups
- Manual: Use `mongodump` for exports

### Code Backups

- Keep code in GitHub
- Tag releases: `git tag v1.0.0`
- Document deployment process

---

## CI/CD Setup (Optional)

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Trigger Render Deploy
        run: curl ${{ secrets.RENDER_DEPLOY_HOOK }}
```

---

## Success Checklist

- [ ] Backend deployed and accessible
- [ ] Health endpoint returns 200
- [ ] API documentation loads
- [ ] Can create account
- [ ] Can login
- [ ] Can start interview session
- [ ] AI generates questions
- [ ] Sessions saved to database
- [ ] Dashboard returns data
- [ ] CORS configured for frontend
- [ ] Environment variables set
- [ ] Monitoring configured
- [ ] Backup strategy in place

---

## Next Steps

1. ✅ Backend deployed
2. ✅ Update frontend `VITE_API_BASE_URL` to production URL
3. ✅ Deploy frontend to Vercel
4. ✅ Test end-to-end flow
5. ✅ Monitor logs and errors
