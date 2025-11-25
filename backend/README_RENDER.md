EcoSync Backend - Render Deployment Guide
----------------------------------------

This backend is a Flask app intended to be deployed to Render (https://render.com) as a Python Web Service.

Steps to deploy on Render:
1. Create a GitHub repository and push the 'backend' folder contents.
2. Log in to Render and create a new Web Service.
   - Connect your GitHub repo and choose the backend folder (or root where app.py is).
   - Build command: pip install -r requirements.txt
   - Start command: gunicorn app:app -b 0.0.0.0:$PORT
3. Add environment variables in Render dashboard:
   - WAQI_TOKEN = <your WAQI token from https://aqicn.org/api/>
4. Deploy. After deploy, Render provides a public URL: e.g., https://ecosync-backend.onrender.com
5. Use that URL for the mobile app BASE setting: https://<YOUR_RENDER_URL>

Notes:
- The app uses a local SQLite DB (db.sqlite). For production, consider PostgreSQL; Render offers managed Postgres.
- To seed demo data, run 'python seed_data.py' locally before push, or adapt to run on startup.
