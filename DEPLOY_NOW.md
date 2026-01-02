# 🚀 Quick Deploy Guide - 5 Minutes!

## Step 1: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `rural-connect` (or any name)
3. Make it **Public**
4. Click **"Create repository"**
5. **Copy the repository URL** (you'll need it)

---

## Step 2: Push Code to GitHub

Run these commands in your terminal:

```bash
cd /home/sandhyam/new-xyz

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "RuralConnect - Rural Services Marketplace"

# Add your GitHub repository (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/rural-connect.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

---

## Step 3: Deploy on Vercel

1. **Go to:** https://vercel.com
2. **Sign up/Login** (use GitHub - easiest!)
3. **Click "Add New..." → "Project"**
4. **Import your repository** (`rural-connect`)
5. **Configure:**

   **Root Directory:** Leave as root (don't change)
   
   **Framework Preset:** Vite (auto-detected)
   
   **Build Settings:**
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
   - Install Command: `cd frontend && npm install`

6. **Environment Variables** - Click "Environment Variables" and add:

   | Name | Value |
   |------|-------|
   | `MONGODB_URI` | `mongodb+srv://sandhyamanjunathn_db_user:TpeVn4BoJkALrP7F@cluster0.owxos1o.mongodb.net/rural_services?retryWrites=true&w=majority` |
   | `JWT_SECRET` | `1xORP_jaDQEvigdlLGvG9VVqeQ2wUoPuzRSz7__cwz8` |

   **Important:** Add for Production, Preview, AND Development!

7. **Click "Deploy"** 🚀

---

## Step 4: Update API URL After Deployment

After Vercel gives you a URL (like `https://rural-connect.vercel.app`):

1. Go to Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Add new variable:
   - Name: `VITE_API_URL`
   - Value: `https://your-app-name.vercel.app/api`
   - (Replace with your actual Vercel URL)
3. **Redeploy** (Vercel will auto-redeploy)

---

## ✅ Done!

Your app is now live at: `https://your-app-name.vercel.app`

**Share this URL with everyone!** 🌍

---

## 🔧 If Something Goes Wrong

**Check:**
1. Vercel build logs (in dashboard)
2. Environment variables are set correctly
3. MongoDB Atlas cluster is running
4. GitHub repository is public

**Need help?** Check `DEPLOY_TO_VERCEL.md` for detailed guide!

