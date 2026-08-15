# Production Deployment Guide: TechMart Multi-Agent AI Support

This guide provides step-by-step instructions for deploying the **Multi-Agent AI Customer Support Assistant** into production:
- **Backend API:** [Render](https://render.com) (FastAPI + Docker + FAISS + Gemini LLM)
- **Frontend App:** [Vercel](https://vercel.com) (Next.js 14 + Tailwind CSS + Lucide)
- **Database:** [Supabase](https://supabase.com) or [Neon](https://neon.tech) / [Render PostgreSQL](https://render.com/docs/databases)

---

## 🏗️ Architecture Overview

```mermaid
flowchart LR
    subgraph Client
        Browser[Client Browser]
    end

    subgraph Vercel ["Frontend (Vercel)"]
        NextApp["Next.js 14 App<br/>(React, Lucide, Tailwind)"]
    end

    subgraph Render ["Backend (Render Web Service)"]
        FastAPI["FastAPI App<br/>(Docker Container)"]
        Router["Intent Router & Orchestrator"]
        Agents["Specialized Agents<br/>(Billing, Tech, Product, Complaint, FAQ)"]
        FAISS["FAISS Vector Store<br/>(MiniLM-L6-v2)"]
    end

    subgraph External ["External Services"]
        Supabase[("PostgreSQL Database<br/>(Supabase / Neon)")]
        Gemini["Google Gemini 1.5 Pro / Flash API"]
    end

    Browser -->|HTTPS| NextApp
    NextApp -->|REST / JWT| FastAPI
    FastAPI --> Router
    Router --> Agents
    Agents --> FAISS
    Agents --> Gemini
    FastAPI --> Supabase
```

---

## 📋 Prerequisites & Required Secrets

Before beginning deployment, ensure you have:
1. A **GitHub account** with this repository pushed.
2. A **Google AI Studio API Key** (`GEMINI_API_KEY`) from [https://aistudio.google.com/app/api-keys](https://aistudio.google.com/app/api-keys).
3. A **PostgreSQL database connection string** (`DATABASE_URL`) from [Supabase](https://supabase.com), [Neon](https://neon.tech), or Render.
4. A **Render account** ([https://render.com](https://render.com)).
5. A **Vercel account** ([https://vercel.com](https://vercel.com)).

---

## 🗄️ Step 1: Database Setup (Supabase / Cloud PostgreSQL)

1. Create a new project in **Supabase** or **Neon**.
2. Copy the **URI Connection String** (format: `postgresql://user:password@host:port/dbname`).
3. If using Supabase Connection Pooler (recommended for serverless/containers), use port `6543` or `5432` with transaction mode.
4. Ensure tables are created either through the initial backend migration or automatic SQLAlchemy initialization on startup.

---

## 🚀 Step 2: Backend Deployment on Render

### Method A: One-Click Blueprint Deployment (Recommended)

1. Log in to **[Render Dashboard](https://dashboard.render.com)**.
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository.
4. Render will detect `render.yaml` inside `customer-support-ai/render.yaml` (or in repository root).
5. Fill in the required environment variable values:
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
   - `DATABASE_URL`: Your PostgreSQL connection string.
   - `FRONTEND_URL`: `https://your-app.vercel.app` (or temporary placeholder `http://localhost:3000`).
   - `CORS_ORIGINS`: `https://your-app.vercel.app`.
6. Click **Apply**. Render will automatically build the Docker image, run the startup healthcheck, and deploy your web service.

---

### Method B: Manual Web Service Deployment

1. Click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Configure the service settings:
   - **Name:** `techmart-support-backend`
   - **Region:** Choose closest to your database (e.g., `Oregon (US West)` or `Frankfurt (EU)`).
   - **Root Directory:** `customer-support-ai` (if repository root contains parent folder).
   - **Runtime:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Instance Type:** `Standard` or `Starter` (512MB+ RAM recommended for sentence-transformers & FAISS).
   - **Health Check Path:** `/health`
4. Under **Environment Variables**, add:

| Key | Value / Description |
|---|---|
| `GEMINI_API_KEY` | `AIzaSy...` (Google Gemini API Key) |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `JWT_SECRET_KEY` | Strong random 32-char hex string |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` |
| `FAISS_INDEX_PATH` | `./vectorstore/faiss_index.bin` |
| `FAISS_METADATA_PATH` | `./vectorstore/faiss_metadata.json` |
| `FRONTEND_URL` | `https://your-frontend.vercel.app` |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app,http://localhost:3000` |

5. Click **Deploy Web Service**.
6. Once deployed, note your public Render URL:
   `https://techmart-support-backend.onrender.com`

---

## ⚡ Step 3: Frontend Deployment on Vercel

1. Log in to **[Vercel Dashboard](https://vercel.com/dashboard)**.
2. Click **Add New...** → **Project**.
3. Import your GitHub repository.
4. Configure the project settings:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Edit and select `customer-support-ai/frontend`.
   - **Build Command:** `npm run build` (Default)
   - **Output Directory:** `.next` (Default)
   - **Install Command:** `npm install` (Default)
5. Under **Environment Variables**, add:

| Key | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://techmart-support-backend.onrender.com` (Your Render backend URL) |

6. Click **Deploy**.
7. Vercel will build and deploy your frontend. Note your production URL:
   `https://techmart-support.vercel.app`

---

## 🔄 Step 4: CORS & Connection Verification

1. Go back to your **Render Dashboard** → `techmart-support-backend` → **Environment**.
2. Update `FRONTEND_URL` and `CORS_ORIGINS` with your actual Vercel domain:
   - `FRONTEND_URL`: `https://techmart-support.vercel.app`
   - `CORS_ORIGINS`: `https://techmart-support.vercel.app,http://localhost:3000`
3. Render will auto-redeploy with the new CORS settings.

---

## 📦 Step 5: Knowledge Base & Vector Index on Render

- The container's startup script `start.sh` automatically checks for `vectorstore/faiss_index.bin` and `vectorstore/faiss_metadata.json`.
- If missing on first boot, it triggers `backend/scripts/ingest_documents.py` to ingest all 8 TechMart PDFs and build the FAISS index automatically.
- To re-index or upload new PDFs at runtime, administrators can use the `POST /api/ingest/upload` endpoint.

---

## 📊 Step 6: Log Streaming & Monitoring

1. Open your **Render Dashboard** → select `techmart-support-backend` → **Logs**.
2. You will observe structured real-time logs with colorized formatting:
   ```text
   2026-08-15 10:45:00.123 | INFO | fastapi_app:log_requests_middleware:78 | POST /api/chat/message -> 200 | 850.40ms
   2026-08-15 10:45:00.200 | INFO | intent_detector:adetect:155 | Detected intents: ['billing', 'technical']
   2026-08-15 10:45:00.350 | INFO | base_agent:run:140 | ⚡ [Agent: BILLING] status=success | duration=310.20ms | chunks_retrieved=4
   2026-08-15 10:45:00.820 | INFO | chat_api:send_message:135 | 🎯 [Orchestration Summary] session=f8a2... | total_time=840.10ms
   ```
3. To view probe health, ping:
   `GET https://techmart-support-backend.onrender.com/health`

---

## 🐳 Step 7: Local & Self-Hosted Docker Compose

To run the entire multi-container production stack locally or on a VPS (AWS EC2, DigitalOcean, Hetzner):

```bash
cd customer-support-ai

# Set your Gemini key
export GEMINI_API_KEY="your-gemini-api-key"

# Build and start all 3 containers (Postgres, Backend, Frontend)
docker-compose up --build -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f backend
```

- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

---

## 🧪 Production Verification Checklist

- [x] Backend responds to `GET /health` with `{"status": "healthy", "database": "connected"}`.
- [x] Frontend successfully registers a new user and auto-logs in with JWT stored in localStorage.
- [x] Single-intent queries route to appropriate domain agent and cite knowledge base sources.
- [x] Compound queries (e.g. billing + technical) invoke multiple agents and return a synthesized response.
- [x] Conversation sessions persist across page refreshes and appear in the sidebar.
- [x] CORS rejects unauthorized origins while accepting the configured Vercel production domain.
