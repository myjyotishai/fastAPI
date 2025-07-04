# JyotishAI Backend (FastAPI)

This is the backend service for the JyotishAI mobile app.

## Endpoints

- `POST /upload/palm` – Analyze palm image
- `POST /upload/face` – Analyze face image
- `POST /rashifal` – Get astrological reading
- `GET /muhurat` – Get lucky time suggestions

## Deployment (Railway or Render)

1. Add `OPENAI_API_KEY` in the environment variables.
2. Use `Procfile` to launch with Uvicorn.
3. Auto deploy from GitHub.
