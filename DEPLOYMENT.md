# 🚀 Deployment Guide - RuralConnect

Complete step-by-step guide to deploy your app for FREE on Vercel.

## 📋 Prerequisites Checklist

- [ ] GitHub account
- [ ] Vercel account (free)
- [ ] MongoDB Atlas account (free)
- [ ] Node.js installed locally
- [ ] Python 3.9+ installed locally

---

## Step 1: MongoDB Atlas Setup (Free Database)

### 1.1 Create Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free" and sign up
3. Choose "Build a Database" → "M0 Free" (Free tier)

### 1.2 Create Cluster
1. Choose a cloud provider (AWS recommended)
2. Select a region closest to you
3. Name your cluster (e.g., "rural-services")
4. Click "Create Cluster" (takes 3-5 minutes)

### 1.3 Database Access
1. Go to "Database Access" in left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create username and password (SAVE THESE!)
5. Set privileges to "Atlas admin" or "Read and write to any database"
6. Click "Add User"

### 1.4 Network Access
1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (0.0.0.0/0)
4. Click "Confirm"

### 1.5 Get Connection String
1. Go to "Database" → "Connect"
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<password>` with your database password
5. Replace `<dbname>` with `rural_services`
6. **SAVE THIS STRING** - You'll need it for Vercel!

Example:
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/rural_services?retryWrites=true&w=majority
```

---

## Step 2: Local Development Setup

### 2.1 Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 2.2 Install Backend Dependencies
```bash
cd api
pip install -r requirements.txt
```

### 2.3 Create Environment Files

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:5000/api
```

**Backend** (`api/.env`):
```env
MONGODB_URI=your_mongodb_atlas_connection_string_here
JWT_SECRET=your-random-secret-key-here
PORT=5000
```

Generate JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.4 Test Locally

**Terminal 1 - Backend:**
```bash
cd api
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit http://localhost:3000

---

## Step 3: Deploy to Vercel

### 3.1 Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - RuralConnect app"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/rural-services-app.git
git branch -M main
git push -u origin main
```

### 3.2 Deploy on Vercel

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** (use GitHub account for easy integration)
3. **Click "New Project"**
4. **Import your GitHub repository**
5. **Configure Project Settings**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

6. **Add Environment Variables**:
   Click "Environment Variables" and add:
   
   | Name | Value |
   |------|-------|
   | `MONGODB_URI` | Your MongoDB Atlas connection string |
   | `JWT_SECRET` | Your JWT secret key |
   | `VITE_API_URL` | Leave empty (will auto-set) |

7. **Deploy!** Click "Deploy"

### 3.3 Update API URL

After deployment, Vercel will give you a URL like:
`https://your-app-name.vercel.app`

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add/Update `VITE_API_URL`:
   ```
   https://your-app-name.vercel.app/api
   ```
3. Redeploy (Vercel will auto-redeploy when you update env vars)

---

## Step 4: Verify Deployment

### 4.1 Test Your App
1. Visit your Vercel URL
2. Try registering a new user
3. Test provider dashboard
4. Test service search

### 4.2 Check Logs
- Vercel Dashboard → Your Project → Functions
- Check for any errors in serverless function logs

---

## 🎉 You're Live!

Your app is now:
- ✅ Hosted on Vercel (free)
- ✅ Using MongoDB Atlas (free)
- ✅ Fully functional with location-based search
- ✅ Accessible from anywhere!

---

## 🔧 Troubleshooting

### Issue: "Database connection failed"
**Solution**: 
- Check MongoDB Atlas connection string
- Verify IP is whitelisted (0.0.0.0/0)
- Check database user credentials

### Issue: "Unauthorized" errors
**Solution**:
- Verify JWT_SECRET is set in Vercel
- Check token is being sent in Authorization header

### Issue: API routes not working
**Solution**:
- Verify `api/` folder structure
- Check Vercel function logs
- Ensure Python runtime is set correctly

### Issue: CORS errors
**Solution**:
- Already handled in backend code
- If persists, check Vercel function configuration

---

## 📊 Monitoring

### Vercel Analytics (Optional)
- Go to Vercel Dashboard → Analytics
- Enable (free tier available)

### MongoDB Atlas Monitoring
- Go to MongoDB Atlas Dashboard
- Check "Metrics" tab for database usage
- Free tier: 512MB storage, enough for thousands of users!

---

## 🚀 Next Steps

1. **Custom Domain** (Optional):
   - Vercel Dashboard → Settings → Domains
   - Add your custom domain (free SSL included)

2. **Add More Features**:
   - Ratings & Reviews
   - Booking System
   - Payment Integration
   - Push Notifications

3. **Scale**:
   - Vercel Pro (if needed) - $20/month
   - MongoDB Atlas M10 (if needed) - $57/month
   - But free tier works great for MVP!

---

## 💡 Tips

- Always test locally before deploying
- Keep environment variables secure
- Monitor MongoDB Atlas usage
- Use Vercel preview deployments for testing
- Enable Vercel Analytics for insights

---

**Need Help?** Check Vercel docs: https://vercel.com/docs

