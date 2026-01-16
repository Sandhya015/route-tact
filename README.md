#  Rural Services Marketplace - "RuralConnect"

A location-based marketplace connecting rural service providers (Tractors, JCBs, Autos, etc.) with customers in rural areas.

## 🎨 Design Features
- **Dark/Light Theme** with blue & purple color scheme
- **Glassmorphism UI** design
- **Enterprise-level** user-friendly interface
- **Fully responsive** mobile-first design

## 🛠️ Tech Stack

### Frontend
- **React 18** + **Vite**
- **Tailwind CSS** (with custom theme)
- **React Router** for navigation
- **Context API** for theme management

### Backend
- **Vercel Serverless Functions** (Python)
- **Flask** (for local development)
- **PyMongo** for MongoDB connection

### Database
- **MongoDB Atlas** (Free Tier)

### Hosting (100% Free)
- **Frontend**: Vercel
- **Backend**: Vercel Serverless Functions
- **Database**: MongoDB Atlas Free Tier

## 📁 Project Structure

```
rural-services-app/
├── frontend/              # React + Vite app
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── context/       # Theme & Auth context
│   │   ├── utils/         # Helper functions
│   │   └── styles/        # Global styles
│   └── package.json
├── api/                   # Vercel serverless functions
│   ├── auth/
│   ├── services/
│   ├── users/
│   └── utils/
├── vercel.json            # Vercel configuration
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- Node.js 18+ installed
- Python 3.9+ installed
- MongoDB Atlas account (free)

### 1. MongoDB Atlas Setup (Free)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free account
3. Create a new cluster (Free M0 tier)
4. Create database user
5. Whitelist IP (0.0.0.0/0 for development)
6. Get connection string

### 2. Environment Variables

Create `.env` files:

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:5000/api
```

**Backend** (`api/.env`):
```env
MONGODB_URI=your_mongodb_atlas_connection_string
JWT_SECRET=your_secret_key_here
```

**For Vercel Deployment**:
- Add these in Vercel Dashboard → Project Settings → Environment Variables

### 3. Install Dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd api
pip install -r requirements.txt
```

### 4. Run Locally

**Frontend:**
```bash
cd frontend
npm run dev
```

**Backend (Local testing):**
```bash
cd api
python app.py
```

### 5. Deploy to Vercel (100% Free)

#### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-github-repo-url
git push -u origin main
```

#### Step 2: Deploy to Vercel
1. Go to [Vercel](https://vercel.com) and sign up/login
2. Click "New Project"
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variables in Vercel Dashboard:
   - `MONGODB_URI`: Your MongoDB Atlas connection string
   - `JWT_SECRET`: A random secret key (e.g., generate with `openssl rand -base64 32`)
   - `VITE_API_URL`: Will be auto-set to your Vercel domain (e.g., `https://your-app.vercel.app/api`)
6. Deploy!

#### Step 3: Update Frontend API URL
After deployment, update `frontend/.env.production`:
```env
VITE_API_URL=https://your-app.vercel.app/api
```

#### Important Notes:
- Vercel automatically detects Python files in `api/` folder as serverless functions
- Each `.py` file in `api/` becomes a serverless function endpoint
- MongoDB Atlas free tier gives you 512MB storage (enough for thousands of users)
- Vercel free tier includes 100GB bandwidth/month

## 📱 Features

### Phase 1 (MVP)
- ✅ User Registration/Login (Provider & Customer)
- ✅ Service Provider Dashboard
- ✅ Add Services (Tractor, JCB, Auto, etc.)
- ✅ Location-based Search
- ✅ Nearby Services Display
- ✅ Contact Details (Call/WhatsApp)
- ✅ Dark/Light Theme Toggle

### Phase 2 (Future)
- Ratings & Reviews
- Booking System
- Price Negotiation
- WhatsApp Integration
- Admin Dashboard

## 🎨 Theme Colors

**Dark Theme:**
- Primary: Blue (#3B82F6)
- Secondary: Purple (#8B5CF6)
- Background: Dark (#0F172A)
- Glass: rgba(30, 41, 59, 0.5)

**Light Theme:**
- Primary: Blue (#2563EB)
- Secondary: Purple (#7C3AED)
- Background: Light (#F8FAFC)
- Glass: rgba(255, 255, 255, 0.7)

## 📝 License

MIT License

## 👨‍💻 Author

Sandhya

