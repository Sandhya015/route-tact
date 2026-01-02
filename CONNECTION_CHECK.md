# 🔌 Database Connection Check

## How to Verify Everything is Connected

### Step 1: Check Environment Variables

Make sure you have `api/.env` file with:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/rural_services?retryWrites=true&w=majority
JWT_SECRET=your-secret-key-here
```

### Step 2: Test Database Connection

```bash
cd api
python test_connection.py
```

**Expected Output:**
```
🔍 Testing MongoDB connection...
MONGODB_URI set: Yes

✅ Connected to MongoDB successfully
   Users collection: 0 documents
   Services collection: 0 documents
   Services indexes: 4 indexes

🎉 Database is ready to use!
```

### Step 3: Test API Endpoints

**Start Backend:**
```bash
cd api
python app.py
```

**Test Registration (in another terminal):**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123",
    "phone": "1234567890",
    "village": "Test Village",
    "district": "Test District",
    "role": "customer"
  }'
```

**Expected Response:**
```json
{
  "message": "Registration successful",
  "token": "eyJ...",
  "user": {
    "_id": "...",
    "name": "Test User",
    "email": "test@example.com",
    ...
  }
}
```

### Step 4: Test Frontend Connection

**Start Frontend:**
```bash
cd frontend
npm run dev
```

1. Open http://localhost:3000
2. Try to register a new user
3. Check browser console (F12) for any errors
4. Check backend terminal for API calls

---

## 🔧 Troubleshooting

### Issue: "Database connection failed"

**Solutions:**
1. ✅ Check `MONGODB_URI` in `api/.env`
2. ✅ Verify MongoDB Atlas cluster is running
3. ✅ Check IP whitelist (should include `0.0.0.0/0`)
4. ✅ Verify database user credentials
5. ✅ Test connection: `python api/test_connection.py`

### Issue: "MONGODB_URI not set"

**Solution:**
- Create `api/.env` file
- Add your MongoDB Atlas connection string

### Issue: "Connection timeout"

**Solutions:**
1. Check internet connection
2. Verify MongoDB Atlas cluster is not paused
3. Check firewall settings
4. Try connection string format:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/rural_services?retryWrites=true&w=majority
   ```

### Issue: "Authentication failed"

**Solutions:**
1. Verify username and password in connection string
2. Check database user has correct permissions
3. URL encode special characters in password

### Issue: Frontend can't connect to API

**Solutions:**
1. Check `VITE_API_URL` in `frontend/.env`
2. Verify backend is running on port 5000
3. Check CORS settings (already configured)
4. Check browser console for errors

---

## ✅ Connection Checklist

- [ ] MongoDB Atlas account created
- [ ] Cluster created and running
- [ ] Database user created
- [ ] IP whitelisted (0.0.0.0/0)
- [ ] Connection string copied
- [ ] `api/.env` file created with MONGODB_URI
- [ ] `python api/test_connection.py` succeeds
- [ ] Backend starts without errors
- [ ] Frontend can make API calls
- [ ] Registration works
- [ ] Login works

---

## 🚀 For Vercel Deployment

When deploying to Vercel:

1. Add environment variables in Vercel Dashboard:
   - `MONGODB_URI`: Your MongoDB Atlas connection string
   - `JWT_SECRET`: Your secret key

2. Vercel will automatically:
   - Connect to MongoDB on each serverless function call
   - Use lazy connection (connects when needed)
   - Handle connection pooling

3. Test after deployment:
   - Visit your Vercel URL
   - Try registering a user
   - Check Vercel function logs for errors

---

## 📊 Connection Status Indicators

**Backend Terminal:**
- ✅ `Connected to MongoDB successfully` = Working
- ❌ `Failed to connect to MongoDB` = Check connection string

**API Response:**
- ✅ `200 OK` with data = Working
- ❌ `500 Database connection failed` = Check MongoDB

**Frontend:**
- ✅ User registered/login works = Everything connected
- ❌ Network errors in console = Check API URL

---

**Need more help?** Check the main `README.md` or `DEPLOYMENT.md`

