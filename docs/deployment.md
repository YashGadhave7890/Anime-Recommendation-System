# ANIMORA — Production Deployment Guide

This document outlines the step-by-step production deployment procedure for deploying the **ANIMORA** full-stack platform:
- **Backend**: FastAPI on **Render** with an attached persistent disk for SQLite
- **Frontend**: React 18 / Vite SPA on **Vercel** with global CDN caching and client-side routing rewrites

---

## 1. System Architecture in Production

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Production Architecture                         │
└────────────────────────────────────────────────────────────────────────┘

    [ Users / Browsers ]
             │
             │ HTTPS (Static Web Assets)
             ▼
    ┌───────────────────────────────────┐
    │     Frontend Hosting (Vercel)     │
    │  • Vite React 18 SPA              │
    │  • Client-Side Routing Rewrites   │
    │  • Global CDN asset distribution  │
    └─────────────────┬─────────────────┘
                      │
                      │ HTTPS REST API Requests (CORS enabled)
                      ▼
    ┌───────────────────────────────────┐
    │     Backend Web Service (Render)  │
    │  • FastAPI + Uvicorn ASGI Server  │
    │  • In-Memory ML Sparse Models     │
    │    (~9.25 MB disk, ~280 MB RAM)   │
    └─────────────────┬─────────────────┘
                      │
                      ▼
    ┌───────────────────────────────────┐
    │   Persistent Disk Storage         │
    │  • SQLite at /var/data/animora.db │
    │    (Preserves ratings/watchlists) │
    └───────────────────────────────────┘
```

---

## 2. Resource Requirements & Platform Constraints

| Component | Resource Requirement | Free/Starter Tier Viability |
|---|---|---|
| **Frontend (Vercel)** | ~1.5 MB static assets | **100% Free** on Vercel Hobby tier. Fast CDN edge routing. |
| **Backend (Render)** | ~280 MB RAM | **Viable on Render Starter/Standard** (512 MB+). Free tier instances spin down after 15 minutes of inactivity, causing a ~30–50s delay on the first incoming request while Python boots and models warm up. |
| **Database (Render Disk)** | ~25 MB SQLite database | Requires a **Render Persistent Disk** mounted at `/var/data` (1 GB disk size) so that user ratings and watchlist additions persist across container redeployments. |

> [!IMPORTANT]
> **Deployment Order**: Deploy the **Backend on Render FIRST**. Only after your backend is running and you have its live URL (e.g. `https://animora-api.onrender.com`) can you configure `VITE_API_BASE_URL` in Vercel and deploy the frontend.

---

## 3. Backend Deployment — Render (Step-by-Step)

Follow these 10 steps to deploy the FastAPI recommendation service to Render:

### Step 1: Create Web Service
Log into the [Render Dashboard](https://dashboard.render.com) and click **New +** $\to$ **Web Service**.

### Step 2: Connect GitHub Repository
Select your `Anime-Recommendation-System` repository and click **Connect**.

### Step 3: Configure Service Basics & Root Directory
- **Name**: `animora-api` (or your preferred service name)
- **Region**: Select the region nearest your users (e.g. `Oregon (US West)` or `Frankfurt (EU Central)`)
- **Branch**: `main`
- **Root Directory**: Leave blank (root of repository)

### Step 4: Configure Runtime & Build Commands
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
  ```

### Step 5: Configure Environment Variables
In the **Environment Variables** section, add:
- `PYTHON_VERSION`: `3.11.9`
- `ENVIRONMENT`: `production`
- `DATABASE_URL`: `sqlite:////var/data/animora.db`
- `CORS_ORIGINS`: `http://localhost:5173,http://127.0.0.1:5173` *(You will append your Vercel URL in Step 10)*

### Step 6: Configure Persistent Disk
Scroll down to **Disks** and click **Add Disk**:
- **Name**: `animora-sqlite-data`
- **Mount Path**: `/var/data`
- **Size**: `1 GB`
*(This ensures your SQLite database file `/var/data/animora.db` survives restarts, dyno sleeping, and service redeployments).*

### Step 7: Configure Health Check Path
Expand **Advanced Settings**:
- **Health Check Path**: `/health`
*(Render uses this endpoint to confirm that the server and ML models are healthy before routing traffic).*

### Step 8: Deploy
Click **Create Web Service**. Render will clone the repository, install Python dependencies, seed the catalog on initial run, warm the ML models, and launch Uvicorn.

### Step 9: Verify `/health`
Once the deployment status turns green (**Live**), open your browser or terminal and verify:
```bash
curl https://animora-api.onrender.com/health
```
Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "ml_engine": "loaded",
  "records_loaded": 17495
}
```

### Step 10: Verify API Endpoints & Update CORS
Run the production smoke test against your new Render URL:
```bash
set ANIMORA_API_URL=https://animora-api.onrender.com
python tests/production_smoke_test.py
```
Copy your Render URL (e.g. `https://animora-api.onrender.com`). You will need it for the frontend.

---

## 4. Frontend Deployment — Vercel (Step-by-Step)

Follow these 7 steps to deploy the React 18 SPA to Vercel:

### Step 1: Import Repository
Log into [Vercel](https://vercel.com) and click **Add New...** $\to$ **Project**. Select your `Anime-Recommendation-System` GitHub repository.

### Step 2: Set Root Directory to `frontend`
In the project configuration screen:
- Click **Edit** next to **Root Directory**.
- Select the `frontend` folder and click **Continue**.

### Step 3: Configure Vite Build Settings
Vercel will automatically detect the **Vite** preset:
- **Framework Preset**: `Vite`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Step 4: Add `VITE_API_BASE_URL` Environment Variable
In the **Environment Variables** accordion:
- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://animora-api.onrender.com` *(Use the exact Render backend URL from Step 10 above, without trailing slash)*

### Step 5: Deploy
Click **Deploy**. Vercel will install dependencies, execute `vite build`, and publish your optimized static bundle to its global CDN.

### Step 6: Verify SPA Routes & Refresh
Click the generated Vercel deployment domain (e.g. `https://animora-discovery.vercel.app`).
Verify that the rewrite rules in `frontend/vercel.json` are working properly:
- Navigate to `/discover` and press browser **Refresh (F5)**. It should reload cleanly without a 404.
- Navigate to `/anime/5114` and refresh.
- Navigate to `/recommendations` and test the ML hybrid sliders.

### Step 7: Update Render Backend CORS Origins
Now that your Vercel URL is known (e.g. `https://animora-discovery.vercel.app`):
1. Return to your **Render Dashboard** $\to$ `animora-api` $\to$ **Environment**.
2. Edit `CORS_ORIGINS` to include your Vercel domain:
   ```text
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://animora-discovery.vercel.app
   ```
3. Save changes. Render will quickly restart the service with the updated CORS policy.

---

## 5. Alternative: Containerized Deployment (Docker)

If hosting on AWS ECS, DigitalOcean App Platform, or Google Cloud Run:

```bash
# Build the production container
docker build -t animora-api:latest .

# Run with port mapping and persistent volume
docker run -d -p 8000:8000 \
  -e PORT=8000 \
  -e CORS_ORIGINS="http://localhost:5173,https://your-vercel-domain.app" \
  -v animora_volume:/app/data \
  --name animora-api animora-api:latest
```

---

## 6. Pre-Flight Deployment Checklist

- [x] Model artifacts checked into `ml/models/` (9.25 MB total, no Git LFS required).
- [x] Processed dataset checked into `data/processed/cleaned_anime.parquet` (11.4 MB).
- [x] Database seeder executes idempotently without overwriting existing data (`force=False`).
- [x] Dynamic `$PORT` resolution tested in backend configuration.
- [x] Healthcheck endpoint (`GET /health`) verifies both database and ML engine readiness.
- [x] `frontend/vercel.json` and `frontend/public/_redirects` configured for SPA routing.
- [x] `frontend/src/api/client.js` uses `VITE_API_BASE_URL` with local dev fallback.
- [x] Automated test suite passing 100% (`51 / 51 passed`).
- [x] Production smoke test script available (`tests/production_smoke_test.py`).
