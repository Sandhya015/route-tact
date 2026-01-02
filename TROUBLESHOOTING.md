# Troubleshooting Vercel Deployment

## Internal Server Error Fixes

### 1. Check Environment Variables

Go to **Vercel Dashboard → Your Project → Settings → Environment Variables** and ensure these are set:

```
MONGODB_URI=mongodb+srv://sandhyamanjunathn_db_user:TpeVn4BoJkALrP7F@cluster0.owxos1o.mongodb.net/?appName=Cluster0
JWT_SECRET=your-random-secret-key-here
```

**Generate JWT_SECRET:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Check Deployment Logs

1. Go to **Vercel Dashboard → Your Project → Deployments**
2. Click on the latest deployment
3. Check the **Build Logs** and **Function Logs** for errors

### 3. Verify API Endpoint

Test your API:
```bash
curl https://your-app.vercel.app/api/test
```

Expected response:
```json
{"message": "API is working!", "db_connected": true}
```

### 4. Common Issues

#### Issue: "Database connection failed"
- **Solution**: Check `MONGODB_URI` is set correctly in Vercel environment variables

#### Issue: "Module not found"
- **Solution**: Ensure `requirements.txt` is in the `api/` folder and includes all dependencies

#### Issue: "Unauthorized" errors
- **Solution**: Check `JWT_SECRET` is set in Vercel environment variables

### 5. Test Locally First

Before deploying, test locally:
```bash
cd api
python app.py
```

Then test:
```bash
curl http://localhost:5000/api/test
```

### 6. Check Vercel Function Logs

1. Go to **Vercel Dashboard → Your Project → Functions**
2. Click on `/api/index.py`
3. Check **Logs** tab for runtime errors

### 7. Verify vercel.json

Ensure `vercel.json` routes `/api/*` to `/api/index.py`:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

## Still Having Issues?

1. Check Vercel's deployment logs for specific error messages
2. Verify all environment variables are set
3. Ensure `requirements.txt` has all dependencies
4. Test the API endpoint directly using curl or Postman

