# 🚀 Quick Start Guide

Get your RuralConnect app running in 5 minutes!

## ⚡ Fast Setup

### 1. Install Dependencies

```bash
# Frontend
cd frontend
npm install

# Backend (in new terminal)
cd api
pip install -r requirements.txt
```

### 2. Setup MongoDB Atlas (5 minutes)

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up (free)
3. Create M0 Free cluster
4. Create database user (save password!)
5. Whitelist IP: `0.0.0.0/0`
6. Get connection string

### 3. Create Environment Files

**`api/.env`:**
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/rural_services?retryWrites=true&w=majority
JWT_SECRET=your-random-secret-key-here
PORT=5000
```

**`frontend/.env`:**
```env
VITE_API_URL=http://localhost:5000/api
```

### 4. Run Locally

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

### 5. Open Browser

Visit: http://localhost:3000

🎉 **You're done!**

---

## 📱 Test the App

1. **Register** as a Provider
2. **Add a Service** (Tractor, JCB, etc.)
3. **Register** as a Customer (use different email)
4. **Search** for services near you
5. **Call/WhatsApp** providers directly

---

## 🚀 Deploy to Vercel

See `DEPLOYMENT.md` for detailed instructions.

**Quick Deploy:**
1. Push to GitHub
2. Import in Vercel
3. Add environment variables
4. Deploy!

---

## 🎨 Features Included

✅ Dark/Light Theme Toggle  
✅ Glassmorphism UI Design  
✅ Blue & Purple Color Scheme  
✅ User Authentication (JWT)  
✅ Provider Dashboard  
✅ Location-based Search  
✅ Service Management  
✅ Direct Contact (Call/WhatsApp)  

---

## 📁 Project Structure

```
rural-services-app/
├── frontend/          # React + Vite app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── ...
│   └── package.json
├── api/               # Python Flask backend
│   ├── auth/
│   ├── services/
│   ├── users/
│   └── utils/
├── vercel.json        # Vercel config
└── README.md
```

---

## 🆘 Need Help?

- Check `DEPLOYMENT.md` for deployment
- Check `README.md` for full documentation
- MongoDB issues? Check Atlas dashboard
- API errors? Check terminal logs

---

**Happy Coding! 🚜**

