EcoSync - Full Project (Render-ready)
====================================

Contents:
- backend/   : Flask backend (use Procfile, gunicorn). Configure WAQI_TOKEN env var on Render.
- mobile/    : Expo React Native app. After backend deploy, set BASE URL in mobile/src/api.js

Quick deploy backend to Render:
1. Create a Git repo and push the 'backend' folder.
2. In Render, create a new Web Service -> Connect to GitHub -> Choose repo.
3. Set build command: pip install -r requirements.txt
4. Start command: gunicorn app:app -b 0.0.0.0:$PORT
5. Add WAQI_TOKEN as environment variable in Render.

After deploy, update mobile/src/api.js BASE to the Render public URL.

