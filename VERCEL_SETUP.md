# Vercel Setup Instructions

## ✅ Fixed Issues

1. **Deleted old individual API files** - All routes now go through `/api/index.py`
2. **Added `requirements.txt` to root** - Vercel will auto-install Python dependencies
3. **Fixed routing** - All `/api/*` requests route to `/api/index.py`

## 🔧 Vercel Configuration

### 1. Environment Variables

Go to **Vercel Dashboard → Your Project → Settings → Environment Variables** and add:

```
MONGODB_URI=mongodb+srv://sandhyamanjunathn_db_user:TpeVn4BoJkALrP7F@cluster0.owxos1o.mongodb.net/?appName=Cluster0
JWT_SECRET=<generate-a-random-secret-key>
```

**Generate JWT_SECRET:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Project Structure

Vercel will automatically:
- Detect Python files in `api/` folder
- Install dependencies from `requirements.txt` (root or api/)
- Route `/api/*` to `/api/index.py` (via vercel.json)

### 3. After Deployment

1. Wait for deployment to complete
2. Test: `https://your-app.vercel.app/api/test`
3. Should return: `{"message": "API is working!", "db_connected": true}`

### 4. If Still Getting Errors

1. **Clear Vercel cache**: Go to Deployments → Redeploy (clear cache)
2. **Check logs**: Vercel Dashboard → Functions → `/api/index.py` → Logs
3. **Verify requirements.txt**: Should be in root directory

## 📝 Current Structure

```
/
├── api/
│   ├── index.py          ← Main handler (all routes)
│   ├── utils/            ← Helper functions
│   └── requirements.txt  ← Python dependencies
├── frontend/             ← React app
├── requirements.txt      ← Also in root (for Vercel)
└── vercel.json          ← Routing config
```

## 🚀 Deployment Status

After pushing to GitHub, Vercel will:
1. Auto-detect changes
2. Install Python dependencies from `requirements.txt`
3. Build frontend
4. Deploy both frontend and API

