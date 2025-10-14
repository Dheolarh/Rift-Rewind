# 🎮 Frontend-Backend Integration Guide

## ✅ **What We've Built**

### **1. Backend Updates**
- ✅ API Service (`api.py`) - Handles all frontend requests
- ✅ Flask Development Server (`server.py`) - Runs on `http://localhost:8000`
- ✅ Match Analysis Capping - Max 300 matches analyzed (intelligent sampling if > 300)
- ✅ CORS enabled for frontend connection

### **2. Frontend Updates**
- ✅ API Service Layer (`src/services/api.ts`) - TypeScript client for backend
- ✅ Custom Loading Messages (5 stages)
- ✅ Loading Slide with Player Name
- ✅ "BEGIN YOUR REWIND" button after analysis completes
- ✅ Error handling and state management

---

## 🚀 **How to Test the Integration**

### **Step 1: Start the Backend**

```powershell
# Navigate to backend folder
cd C:\Users\Administrator\Desktop\Rift-Rewind\backend

# Activate virtual environment
..\venv\Scripts\Activate.ps1

# Install dependencies (if not already done)
pip install -r requirements.txt

# Set your Riot API key in .env file
# Edit backend/.env and add your key:
# RIOT_API_KEY=RGAPI-your-key-here

# Start Flask server
python server.py
```

You should see:
```
╔══════════════════════════════════════════════════════════╗
║  RIFT REWIND - Development API Server                   ║
╚══════════════════════════════════════════════════════════╝

Server running at: http://localhost:8000
```

### **Step 2: Start the Frontend**

Open a NEW terminal:

```powershell
# Navigate to frontend folder
cd C:\Users\Administrator\Desktop\Rift-Rewind\frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### **Step 3: Test the Flow**

1. **Open browser**: Go to `http://localhost:5173`

2. **Welcome Screen**: 
   - Enter Summoner Name (e.g., "Hide on bush")
   - Enter Tag (e.g., "KR1")
   - Select Region (e.g., "Korea")
   - Click "START YOUR RIFT REWIND"

3. **Loading Screen** (Watch the messages):
   ```
   1. "Connecting to the Rift..."
   2. "Connected"
   3. "Checking how much chaos you caused..."
   4. "Hmmm [YourName] right?"
   5. "I see......"
   ```

4. **Backend Processing**:
   - Backend fetches player data
   - Analyzes matches (max 300)
   - Generates analytics
   - Creates AI humor (in test mode)

5. **Analysis Complete**:
   - "BEGIN YOUR REWIND" button appears
   - Click to view slides

6. **Slides Available**:
   - Slide 2: Time Spent
   - Slide 3: Favorite Champions

---

## 🔧 **Backend API Endpoints**

### Health Check
```bash
GET http://localhost:8000/api/health
```
Response:
```json
{
  "status": "healthy",
  "testMode": false,
  "maxMatches": 300
}
```

### Get Regions
```bash
GET http://localhost:8000/api/regions
```

### Start Rewind
```bash
POST http://localhost:8000/api/rewind
Content-Type: application/json

{
  "gameName": "Hide on bush",
  "tagLine": "KR1",
  "region": "kr"
}
```

Response:
```json
{
  "sessionId": "uuid-here",
  "status": "complete",
  "testMode": false,
  "matchCount": 300,
  "player": {
    "gameName": "Hide on bush",
    "tagLine": "KR1",
    "region": "kr",
    "summonerLevel": 250,
    "rank": "PLATINUM II"
  }
}
```

### Get Session Data
```bash
GET http://localhost:8000/api/rewind/{sessionId}
```

### Get Slide Data
```bash
GET http://localhost:8000/api/rewind/{sessionId}/slide/2
```

---

## 📊 **Match Analysis Logic**

### Current Behavior:
```
Total Matches Found | Matches Analyzed | Strategy
---------------------|------------------|------------------
0-300               | All matches      | Full analysis
301-1000            | 300 matches      | Intelligent sampling
1000+               | 300 matches      | Intelligent sampling
```

### Sampling Strategy:
- If ≤300 matches: Analyze all
- If >300 matches: Use `IntelligentSampler` to select 300 representative matches
  - Distributed across months to avoid seasonal bias
  - Ensures recent matches are included
  - Maintains statistical significance

---

## 🐛 **Troubleshooting**

### Backend won't start:
```powershell
# Check if port 8000 is already in use
netstat -ano | findstr :8000

# Kill the process if needed
taskkill /PID <pid> /F

# Check Python environment
python --version  # Should be 3.8+

# Check .env file exists
ls backend/.env
```

### Frontend can't connect to backend:
1. Check backend is running: `http://localhost:8000/api/health`
2. Check CORS settings in `backend/server.py`
3. Check `frontend/.env` has correct `VITE_API_ENDPOINT`
4. Clear browser cache and reload

### Riot API errors:
```
Error: 403 Forbidden
→ API key is invalid or expired
→ Get new key: https://developer.riotgames.com/

Error: 429 Too Many Requests
→ Rate limit exceeded
→ Wait 2 minutes or use TEST_MODE=true

Error: 404 Not Found
→ Summoner doesn't exist
→ Check spelling and region
```

---

## 🎯 **Next Steps**

### Completed:
✅ Backend API service
✅ Frontend API client
✅ Loading screen with custom messages
✅ Match analysis (max 300)
✅ Error handling
✅ State management

### TODO:
⏳ Connect TimeSpent slide to real data
⏳ Connect FavoriteChampions slide to real data
⏳ Complete remaining slides (4-15)
⏳ Add AI humor integration
⏳ Deploy to AWS
⏳ Add caching layer

---

## 📝 **Environment Variables**

### Backend (`backend/.env`)
```bash
RIOT_API_KEY=RGAPI-your-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=rift-rewind-sessions
TEST_MODE=false
ALLOWED_ORIGINS=http://localhost:5173
PORT=8000
DEBUG=true
```

### Frontend (`frontend/.env`)
```bash
VITE_API_ENDPOINT=http://localhost:8000
```

---

## 🔐 **Security Notes**

1. **Never commit** `.env` files to git
2. **Never expose** Riot API keys in frontend
3. **Always use** environment variables for secrets
4. **Enable** CORS only for trusted origins

---

## 📚 **Testing Examples**

### Test with Known Player:
```json
{
  "gameName": "Hide on bush",
  "tagLine": "KR1",
  "region": "kr"
}
```

### Test with Your Account:
```json
{
  "gameName": "YourSummonerName",
  "tagLine": "NA1",
  "region": "na1"
}
```

---

**🎉 You're ready to test! Start both servers and visit `http://localhost:5173`**
