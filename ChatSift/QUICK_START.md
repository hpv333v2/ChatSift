# ChatSift - Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ and npm installed
- Git (to clone the repository)

---

## Option 1: Automated Setup (Recommended)

### Windows Users

1. **Start Backend:**
   ```cmd
   cd Chatsift\ChatSift\backend
   setup_and_run.bat
   ```
   Wait for "Starting development server at http://127.0.0.1:8000/"

2. **Start Frontend** (in a new terminal):
   ```cmd
   cd Chatsift\ChatSift\frontend\chatsift-frontend
   run_demo.bat
   ```
   Press 'w' when prompted to open in web browser

### Linux/Mac Users

1. **Start Backend:**
   ```bash
   cd Chatsift/ChatSift/backend
   chmod +x setup_and_run.sh
   ./setup_and_run.sh
   ```

2. **Start Frontend** (in a new terminal):
   ```bash
   cd Chatsift/ChatSift/frontend/chatsift-frontend
   npm install --legacy-peer-deps
   npm start
   ```
   Press 'w' to open in web browser

---

## Option 2: Manual Setup

### Backend Setup

```bash
cd Chatsift/ChatSift/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
cd Chatsift/ChatSift/frontend/chatsift-frontend

# Install dependencies
npm install --legacy-peer-deps

# Start Expo
npm start

# Press 'w' to open in web browser
```

---

## 🎯 Testing the App

### 1. Register an Account
- Open http://localhost:8081 in your browser
- Click "Register" or "Sign Up"
- Fill in:
  - Email: test@example.com
  - Username: testuser
  - Password: Test123!@#
  - Confirm Password: Test123!@#

### 2. Verify Email (Development Mode)
- Check the backend terminal/console
- Look for the verification link (it will be printed)
- Copy the token and uid from the link
- Use the verification screen in the app

### 3. Login
- Use your registered credentials
- Email: test@example.com
- Password: Test123!@#

### 4. Explore Features
- **Dashboard:** Overview of your integrations
- **Integrations:** Connect Discord/Telegram (requires setup)
- **Monitoring:** View chat activity
- **Summaries:** AI-generated summaries
- **Settings:** Manage your profile

---

## 🔧 Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'django'"**
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Then install dependencies
pip install -r requirements.txt
```

**"Port 8000 already in use"**
```bash
# Use a different port
python manage.py runserver 8001
# Update frontend API URL accordingly
```

### Frontend Issues

**"npm install fails with ERESOLVE"**
```bash
# Use legacy peer deps flag
npm install --legacy-peer-deps
```

**"Cannot connect to backend"**
- Ensure backend is running at http://localhost:8000
- Check if EXPO_PUBLIC_API_URL is set correctly
- Try accessing http://localhost:8000/api/v1/ in browser

**"Expo not opening in browser"**
```bash
# Press 'w' in the terminal where npm start is running
# Or manually open: http://localhost:8081
```

---

## 📱 Running on Mobile

### Using Expo Go App

1. Install Expo Go on your phone:
   - iOS: App Store
   - Android: Google Play Store

2. Start the frontend:
   ```bash
   npm start
   ```

3. Scan the QR code with:
   - iOS: Camera app
   - Android: Expo Go app

4. Update API URL for mobile:
   - Find your computer's IP address
   - Set EXPO_PUBLIC_API_URL=http://YOUR_IP:8000/api

---

## 🌐 API Endpoints

Backend runs at: **http://localhost:8000**

### Authentication
- POST `/api/v1/auth/register/` - Register new user
- POST `/api/v1/auth/login/` - Login
- POST `/api/v1/auth/logout/` - Logout
- POST `/api/v1/auth/refresh/` - Refresh token

### User Profile
- GET `/api/v1/users/me/` - Get current user
- PATCH `/api/v1/users/me/` - Update profile
- DELETE `/api/v1/users/me/` - Delete account

### Integrations
- GET `/api/v1/integrations/` - List integrations
- GET `/api/v1/integrations/{id}/` - Get integration details
- DELETE `/api/v1/integrations/{id}/` - Disconnect integration

### Admin Panel
- URL: http://localhost:8000/admin
- Create superuser: `python manage.py createsuperuser`

---

## 💡 Tips

1. **Keep both terminals open** - Backend and Frontend need to run simultaneously
2. **Check console logs** - Errors will appear in the terminal
3. **Use web browser first** - Easier for initial testing
4. **Email verification** - In development, links appear in backend console
5. **Hot reload** - Both frontend and backend support hot reload

---

## 📚 Next Steps

- Read `FIXES_APPLIED.md` for technical details
- Check `backend/BACKEND_ARCHITECTURE.md` for backend info
- Review `frontend/FRONTEND_MASTER_PLAN.md` for frontend structure
- Explore API documentation in `backend/accounts/docs/`

---

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review `FIXES_APPLIED.md` for known issues
3. Ensure all prerequisites are installed
4. Verify both backend and frontend are running

---

**Happy Coding! 🎉**