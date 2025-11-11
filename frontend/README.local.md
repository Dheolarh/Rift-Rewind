Local development: run backend + frontend
=====================================

These steps let you run the Flask development backend locally and point the Vite frontend at it for testing.

Prereqs
- Python 3.10+ (or 3.8+)
- Node.js and npm (or pnpm/yarn)

Quick steps (PowerShell)

1) Setup and start the backend

```powershell
# from project root
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
cd backend
python server.py
```

The server runs on port 8000 by default and serves:
- GET  /api/health
- GET  /api/regions
- POST /api/rewind
- GET  /api/rewind/:sessionId

2) Start the frontend (will use local backend)

This project includes `frontend/.env.local` that points Vite to `http://localhost:8000`.

```powershell
cd frontend
npm install
npm run dev
```

If you prefer to set the env var in the shell instead of using `.env.local`, run:

```powershell
$env:VITE_API_BASE_URL = 'http://localhost:8000'
npm run dev
```

Tips & troubleshooting
- If the frontend still calls the remote API, ensure you don't have other env files (`.env.production`) overriding values in the build mode you run.
- Check the browser Network tab for the exact POST URL used by the app and compare it to the backend URL (should be `http://localhost:8000/api/rewind`).
- If CORS errors occur, ensure `backend/server.py` lists `http://localhost:5173` (Vite default) in `ALLOWED_ORIGINS` or run Vite on a port that's allowed.

If you want me to also add a convenience npm script to start both backend and frontend concurrently, tell me and I can add it.
