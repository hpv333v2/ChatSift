# ChatSift - AI-Powered Community Management

**IBM watsonx Code Assistant Hackathon Submission**

## Problem

Community managers drown in thousands of Discord/Telegram messages daily. Critical discussions, bug reports, and feature requests get buried. Founders spend 3+ hours/day manually scanning chats instead of building products.

## Solution

ChatSift transforms message chaos into actionable intelligence. Connect your Discord/Telegram, select channels to monitor, receive AI-generated summaries of what matters. Reduce community management time by 83%.

**Future Vision:** Expand to all major platforms - WhatsApp groups, Instagram DMs/group chats, Slack, Microsoft Teams, and any text-based social communication channel. One unified dashboard for all community conversations.

## Features

- **Multi-Platform Integration** - Discord & Telegram (v1), expanding to WhatsApp, Instagram, Slack, Teams
- **AI Summarization** - Extract key themes, urgent issues, sentiment
- **Smart Prioritization** - Surface critical discussions first
- **Mobile-First** - React Native app for on-the-go management
- **Real-Time Monitoring** - Continuous message analysis
- **Direct Navigation** - Jump to original conversations with one tap

## Tech Stack

**Frontend:** React Native (Expo), TypeScript, Zustand, React Navigation  
**Backend:** Django 6.0.4, Django REST Framework, JWT Auth  
**Database:** SQLite (dev), PostgreSQL (prod)  
**Task Queue:** Celery + Redis  
**APIs:** Discord OAuth, Telegram Bot API

## How to Run

### Backend (Terminal 1)
```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend (Terminal 2)
```powershell
cd frontend\chatsift-frontend
npm install
npm start
```

Press `w` for web browser or scan QR code with Expo Go app.

## Demo Flow

1. **Register Account** - Email: `demo@chatsift.app`, Password: `DemoPass123!`
2. **Verify Email** - Check backend terminal for verification link
3. **View Dashboard** - See summary statistics and recent activity
4. **Navigate to Integrations** - View Discord/Telegram connection cards
5. **Explore Monitoring** - Configure channel selection (UI ready, OAuth pending)
6. **Check Summaries** - View AI-generated message summaries
7. **Update Settings** - Manage profile and preferences

## How IBM Bob Was Used

**Architecture Planning** - Bob designed React Native component structure, state management patterns, and navigation architecture. Recommended Zustand over Redux for simpler state management.

**Backend Integration** - Provided Django REST Framework endpoint design, JWT authentication flow, and axios client configuration with token refresh interceptors.

**Debugging CORS** - Diagnosed persistent CORS errors, explained security implications, provided exact Django middleware configuration that resolved issues while maintaining security.

**AsyncStorage Fix** - Identified incorrect async/await patterns causing data persistence failures. Provided proper implementation for offline message caching.

**Navigation Debugging** - Analyzed React Navigation setup, identified conflicting parameters, recommended cleaner architecture that eliminated routing bugs.

**Demo Data Generation** - Created realistic Discord/Telegram message datasets across technical discussions, bug reports, feature requests. Saved 3-4 hours of manual data creation.

**Time Saved:** 20-27 hours total development time

## Known Limitations

- **OAuth Not Configured** - Discord/Telegram app credentials needed for live integration
- **Email Service** - Uses console backend (check terminal for verification links)
- **AI Summarization** - Placeholder implementation (real NLP integration pending)
- **WebSockets** - Real-time updates use polling (WebSocket implementation planned)
- **Production Config** - DEBUG=True, hardcoded SECRET_KEY (dev only)

## Future Roadmap

**Phase 1 (Q2 2026)** - Complete Discord/Telegram OAuth, real-time WebSockets, advanced AI summarization

**Phase 2 (Q3 2026)** - WhatsApp Business API integration, Instagram messaging API, Slack workspace integration

**Phase 3 (Q4 2026)** - Microsoft Teams, LinkedIn groups, Reddit communities, custom AI training per user

**Phase 4 (2027)** - Universal social media aggregation, cross-platform analytics, team collaboration features

## Team

**Solo Developer** - Built with IBM watsonx Code Assistant (Bob)

---

**Full Documentation:** [`HACKATHON_SUBMISSION.md`](HACKATHON_SUBMISSION.md)  
**Next Steps:** [`NEXT_STEPS.md`](NEXT_STEPS.md)  
**Architecture:** [`backend/BACKEND_ARCHITECTURE.md`](backend/BACKEND_ARCHITECTURE.md)