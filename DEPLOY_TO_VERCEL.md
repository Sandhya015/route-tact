# 🚀 Deploy to Vercel - Step by Step Guide

Deploy your RuralConnect app to Vercel (100% FREE) so it works everywhere!

---

## ✅ Prerequisites

- ✅ GitHub account (free)
- ✅ Vercel account (free)
- ✅ MongoDB Atlas already set up (you have this!)

---

## Step 1: Push Code to GitHub

### 1.1 Initialize Git (if not done)

```bash
cd /home/sandhyam/new-xyz
git init
git add .
git commit -m "Initial commit - RuralConnect app"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `rural-connect` (or any name)
3. Make it **Public** (for free Vercel)
4. Click **"Create repository"**

### 1.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/rural-connect.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your GitHub username!**

---

## Step 2: Deploy on Vercel

### 2.1 Sign Up/Login to Vercel

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"** (easiest!)
4. Authorize Vercel

### 2.2 Import Your Project

1. In Vercel Dashboard, click **"Add New..."** → **"Project"**
2. Find your `rural-connect` repository
3. Click **"Import"**

### 2.3 Configure Project

**Root Directory:** Leave as is (root)

**Framework Preset:** Vite (auto-detected)

**Build Settings:**
- Build Command: `cd frontend && npm install && npm run build`
- Output Directory: `frontend/dist`
- Install Command: `cd frontend && npm install`

### 2.4 Add Environment Variables

Click **"Environment Variables"** and add:

| Name | Value |
|------|-------|
| `MONGODB_URI` | `mongodb+srv://sandhyamanjunathn_db_user:TpeVn4BoJkALrP7F@cluster0.owxos1o.mongodb.net/rural_services?retryWrites=true&w=majority` |
| `JWT_SECRET` | `1xORP_jaDQEvigdlLGvG9VVqeQ2wUoPuzRSz7__cwz8` |
| `VITE_API_URL` | Leave empty (will auto-set) |

**Important:** 
- Add these for **Production**, **Preview**, and **Development**
- Click **"Save"** after adding each

### 2.5 Deploy!

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. You'll get a URL like: `https://rural-connect.vercel.app`

---

## Step 3: Update API URL

After deployment:

1. Go to Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Add/Update `VITE_API_URL`:
   ```
   https://your-app-name.vercel.app/api
   ```
3. **Redeploy** (Vercel will auto-redeploy when you update env vars)

---

## Step 4: Test Your Live App

1. Visit your Vercel URL
2. Test registration
3. Test login
4. Test search
5. Everything should work! 🎉

---

## 🔧 Troubleshooting

### Issue: Build fails

**Solution:**
- Check build logs in Vercel
- Make sure `frontend/package.json` has all dependencies
- Check if `framer-motion` is installed

### Issue: API routes return 404

**Solution:**
- Check `vercel.json` configuration
- Verify Python files are in `api/` folder
- Check Vercel function logs

### Issue: Database connection fails

**Solution:**
- Verify `MONGODB_URI` in Vercel environment variables
- Check MongoDB Atlas IP whitelist (should have 0.0.0.0/0)
- Check MongoDB Atlas cluster is running

### Issue: CORS errors

**Solution:**
- Already handled in backend code
- If persists, check API URL matches Vercel domain

---

## 📝 Quick Commands

```bash
# Push updates to GitHub
git add .
git commit -m "Update app"
git push

# Vercel will auto-deploy on push!
```

---

## 🎉 You're Live!

Your app is now:
- ✅ Accessible from anywhere
- ✅ Free hosting (Vercel + MongoDB Atlas)
- ✅ Auto-deploys on every push
- ✅ HTTPS enabled (free SSL)
- ✅ Fast CDN worldwide

**Share your app URL with everyone!** 🌍

---

## 🔗 Useful Links

- Vercel Dashboard: https://vercel.com/dashboard
- MongoDB Atlas: https://cloud.mongodb.com
- Your App: `https://your-app-name.vercel.app`

---

**Need help?** Check Vercel logs in dashboard for errors!

