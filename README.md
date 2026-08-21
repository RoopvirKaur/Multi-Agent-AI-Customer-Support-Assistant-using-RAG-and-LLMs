# 🤖 Multi-Agent AI Customer Support Assistant

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Pro%2FFlash-4285F4.svg)](https://aistudio.google.com/)
[![FAISS](https://img.shields.io/badge/VectorStore-FAISS-orange.svg)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready, autonomous multi-agent customer support system built for **TechMart Electronics**. Powered by **Google Gemini**, **FastAPI**, **Next.js 14**, and **FAISS** vector search, this assistant dynamically detects user intents, routes queries to domain-specialized AI agents in parallel, retrieves grounded context using RAG (Retrieval-Augmented Generation), and synthesizes unified responses.

---

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [📐 System Architecture](#-system-architecture)
- [🤖 Multi-Agent System Matrix](#-multi-agent-system-matrix)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Repository Structure](#-repository-structure)
- [⚙️ Environment Variables](#️-environment-variables)
- [🚀 Step-by-Step Setup Guide](#-step-by-step-setup-guide)
  - [Prerequisites](#prerequisites)
  - [1. Clone & Environment Config](#1-clone--environment-config)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Database Setup](#3-database-setup)
  - [4. Knowledge Base Ingestion](#4-knowledge-base-ingestion)
  - [5. Run Backend Server](#5-run-backend-server)
  - [6. Run Frontend Application](#6-run-frontend-application)
  - [7. Run with Docker Compose](#7-run-with-docker-compose)
- [📡 API Endpoints](#-api-endpoints)
- [📚 Knowledge Base Documents](#-knowledge-base-documents)
- [🧪 Testing & Evaluation](#-testing--evaluation)
- [🚀 Deployment](#-deployment)
- [📄 License](#-license)

---

## ✨ Key Features

- **🧠 Autonomous Intent Detection**: Classifies queries into `billing`, `technical`, `product`, `complaint`, or `faq` domains (including multi-intent queries).
- **🔀 Parallel Agent Routing**: Spawns multiple specialized agents concurrently using Python `asyncio` to reduce latency.
- **📚 Grounded RAG Pipeline**: Uses local `sentence-transformers` embeddings and FAISS vector index to inject relevant domain context into LLM prompts.
- **🛡️ Conflict & Hallucination Mitigation**: Dedicated **Response Aggregator Agent** validates outputs, removes contradictions, and ensures brand tone consistency.
- **🔐 Secure Authentication & Rate Limiting**: JWT authentication (HS256) with bcrypt password hashing and SlowAPI rate limiting per user IP/token.
- **💬 Persistent Multi-Turn Chat**: Session-based chat history backed by Supabase PostgreSQL database.
- **💻 Modern Next.js 14 UI**: Responsive, real-time chat interface featuring glassmorphism aesthetics, markdown rendering, agent badge tags, and source citations.

---

## 📐 System Architecture

```
                       ┌─────────────────────────┐
                       │       User Query        │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │  Intent Detector Agent  │
                       │     (Google Gemini)     │
                       └────────────┬────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            │  Multi-Intent Router (Async Parallel Tasks)   │
            └───────┬──────────┬───────────┬───────────┬────┘
                    │          │           │           │
                    ▼          ▼           ▼           ▼
               ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
               │Billing │ │Tech    │ │Product │ │Complain│ │FAQ     │
               │Agent   │ │Agent   │ │Agent   │ │Agent   │ │Agent   │
               └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
                   │          │           │           │          │
                   └──────────┼───────────┼───────────┼──────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │   RAG Retrieval Engine       │
               │  (FAISS + MiniLM Embedder)   │
               └──────────────┬───────────────┘
                              │  Retrieved Documents & Context
                              ▼
               ┌──────────────────────────────┐
               │     Google Gemini LLM        │
               │    (Grounded Generation)     │
               └──────────────┬───────────────┘
                              │  Agent Sub-Responses
                              ▼
               ┌──────────────────────────────┐
               │  Response Aggregator Agent   │
               │  (Deduplication & Formatting)│
               └──────────────┬───────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │ Final Answer │
                       └──────────────┘
```

---

## 🤖 Multi-Agent System Matrix

| Agent | Module Path | Scope & Primary Responsibilities |
|---|---|---|
| **Intent Detector** | [`intent_detector.py`](customer-support-ai/backend/agents/intent_detector.py) | Analyzes incoming user messages and detects primary & secondary intents with confidence scores. |
| **Agent Router** | [`router.py`](customer-support-ai/backend/agents/router.py) | Dispatches queries to domain agents concurrently using `asyncio.gather()`. |
| **Billing Agent** | [`billing.py`](customer-support-ai/backend/agents/billing.py) | Handles invoices, payment methods, refund status, subscriptions, and transaction errors. |
| **Technical Agent** | [`technical.py`](customer-support-ai/backend/agents/technical.py) | Troubleshoots installation issues, device errors, firmware updates, and connectivity problems. |
| **Product Agent** | [`product.py`](customer-support-ai/backend/agents/product.py) | Answers queries regarding product specifications, pricing tiers, compatibility, and availability. |
| **Complaint Agent** | [`complaint.py`](customer-support-ai/backend/agents/complaint.py) | Manages customer dissatisfaction, escalations, apology messaging, and priority ticketing. |
| **FAQ Agent** | [`faq.py`](customer-support-ai/backend/agents/faq.py) | Provides instant answers for store hours, shipping policies, warranty terms, and general policies. |
| **Response Aggregator** | [`aggregator.py`](customer-support-ai/backend/agents/aggregator.py) | Combines outputs from multiple agents, eliminates redundant text, and formats structured output. |

---

## 🛠️ Tech Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend** | [Next.js 14](https://nextjs.org/), TypeScript, Tailwind CSS | App Router, React Server Components, Lucide Icons |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/), Python 3.11+, Uvicorn | Async ASGI framework with Pydantic validation |
| **AI / LLM** | [Google Gemini](https://ai.google.dev/) via `langchain-google-genai` | Multi-turn text generation, intent classification & synthesis |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Fast CPU-friendly 384-dimensional dense vector embeddings |
| **Vector Index** | [FAISS](https://github.com/facebookresearch/faiss) | Efficient vector similarity search (L2 distance / Inner Product) |
| **Database** | [PostgreSQL (Supabase)](https://supabase.com/), SQLAlchemy | Async database ORM for users, sessions, and chat logs |
| **Auth & Security** | PyJWT, Passlib (bcrypt), SlowAPI | JWT token-based auth and IP rate limiting |

---

## 📁 Repository Structure

```
.
├── customer-support-ai/              # Main Application Codebase
│   ├── backend/                      # FastAPI Backend
│   │   ├── agents/                   # Multi-agent system (intent, router, 5 sub-agents, aggregator)
│   │   ├── api/                      # FastAPI endpoint handlers (auth, chat, history, ingest)
│   │   ├── database/                 # SQLAlchemy models & CRUD database layer
│   │   ├── embeddings/               # SentenceTransformer embedding service
│   │   ├── llm/                      # Gemini LLM client wrapper
│   │   ├── middleware/               # Auth verification & CORS middleware
│   │   ├── models/                   # Pydantic schemas for request/response validation
│   │   ├── rag/                      # Document chunker & FAISS retriever pipeline
│   │   ├── scripts/                  # Data ingestion & CLI helper scripts
│   │   └── vectorstore/              # FAISS index binary & metadata persistence
│   ├── frontend/                     # Next.js 14 Web UI
│   │   ├── app/                      # Next.js App Router pages (login, register, chat)
│   │   ├── components/               # UI components (ChatWindow, Sidebar, MessageBubble)
│   │   ├── hooks/                    # Custom React hooks
│   │   └── services/                 # API client services (Axios/Fetch wrapper)
│   ├── knowledge_base/               # Synthetic TechMart PDF source documents
│   ├── datasets/                     # Benchmark evaluation datasets
│   ├── docker-compose.yml            # Docker orchestration configuration
│   ├── Dockerfile                    # Container configuration for backend
│   └── requirements.txt              # Python dependency manifest
├── Docs/                             # Architectural Specifications
│   ├── architecture.md               # Deep-dive system architecture specification
│   ├── implementation_plan.md        # 8-Phase engineering roadmap
│   ├── edge_cases.md                 # Edge case handling matrix
│   └── ProblemStatement.txt          # Original problem statement & constraints
├── .gitignore                        # Git ignore patterns
└── README.md                         # Project documentation
```

---

## ⚙️ Environment Variables

Create a `.env` file in the [`customer-support-ai/`](customer-support-ai/) folder (refer to [`customer-support-ai/.env.example`](customer-support-ai/.env.example)):

| Variable | Required | Description | Example |
|---|---|---|---|
| `GEMINI_API_KEY` | **Yes** | Google Gemini API Key | `AIzaSy...` |
| `DATABASE_URL` | **Yes** | PostgreSQL connection URI | `postgresql+asyncpg://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | **Yes** | Secret key for signing JWT tokens | `super-secret-hex-string` |
| `JWT_ALGORITHM` | No | Signing algorithm (Default: `HS256`) | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | JWT token expiry in minutes | `1440` (24h) |
| `EMBEDDING_MODEL` | No | HuggingFace embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| `FAISS_INDEX_PATH` | No | File path to binary FAISS index | `./vectorstore/faiss_index.bin` |
| `FRONTEND_URL` | No | Origin URL for CORS settings | `http://localhost:3000` |

---

## 🚀 Step-by-Step Setup Guide

### Prerequisites

Ensure you have the following installed on your machine:
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher (npm included)
- **Git**
- A **Google Gemini API Key** ([Get one here](https://aistudio.google.com/app/api-keys))
- A **Supabase PostgreSQL** project ([Supabase Signup](https://supabase.com/))

---

### 1. Clone & Environment Config

```bash
# Navigate to project root
cd Multi-Agent-AI-Customer-Support-Assistant-using-RAG-and-LLMs/customer-support-ai

# Create .env from template
cp .env.example .env
```

Open `.env` in your code editor and populate `GEMINI_API_KEY`, `DATABASE_URL`, and `JWT_SECRET_KEY`.

---

### 2. Backend Setup

```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. Database Setup

Execute the database schema setup against your Supabase PostgreSQL instance:
1. Open the Supabase SQL Editor for your project.
2. Run the DDL script found in [`Docs/architecture.md`](Docs/architecture.md) or [`Docs/implementation_plan.md`](Docs/implementation_plan.md) to create the `users`, `conversations`, `messages`, and `feedback` tables.

---

### 4. Knowledge Base Ingestion

Ingest the 8 TechMart Electronics PDF documents from `knowledge_base/` into the FAISS vector index:

```bash
python backend/scripts/ingest_documents.py
```

> [!NOTE]
> This command will chunk PDF files, compute embeddings using `all-MiniLM-L6-v2`, and save the index files to `backend/vectorstore/`.

---

### 5. Run Backend Server

Start the FastAPI application with Uvicorn auto-reload:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

---

### 6. Run Frontend Application

In a new terminal window:

```bash
cd customer-support-ai/frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

- **Frontend App**: `http://localhost:3000`

---

### 7. Run with Docker Compose

Alternatively, launch the full stack (Backend & Frontend) using Docker:

```bash
cd customer-support-ai
docker-compose up --build
```

---

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` — Register new user account.
- `POST /api/v1/auth/login` — Authenticate and obtain JWT access token.
- `GET /api/v1/auth/me` — Retrieve current authenticated user profile.

### Chat & AI Multi-Agent
- `POST /api/v1/chat/message` — Send message to multi-agent pipeline and get grounded response.
- `GET /api/v1/chat/history/{session_id}` — Retrieve conversation history for a specific session.
- `DELETE /api/v1/chat/session/{session_id}` — Delete or clear a chat session.

### Knowledge Base & System
- `POST /api/v1/ingest/upload` — Ingest new PDF document into FAISS vector index (Admin).
- `GET /health` — Service health check endpoint.

---

## 📚 Knowledge Base Documents

The RAG pipeline is pre-populated with synthetic corporate documentation for **TechMart Electronics**:

1. [`FAQ.pdf`](customer-support-ai/knowledge_base/FAQ.pdf): General store info, working hours, and support channels.
2. [`RefundPolicy.pdf`](customer-support-ai/knowledge_base/RefundPolicy.pdf): 30-day return policy guidelines and conditions.
3. [`ShippingPolicy.pdf`](customer-support-ai/knowledge_base/ShippingPolicy.pdf): Standard, expedited, and international shipping rates.
4. [`Warranty.pdf`](customer-support-ai/knowledge_base/Warranty.pdf): Limited 1-year product warranty terms & claims process.
5. [`Pricing.pdf`](customer-support-ai/knowledge_base/Pricing.pdf): Pricing tiers, bulk discounts, and price matching rules.
6. [`Products.pdf`](customer-support-ai/knowledge_base/Products.pdf): Product catalog, specs, and stock status.
7. [`InstallationGuide.pdf`](customer-support-ai/knowledge_base/InstallationGuide.pdf): Setup and setup instructions for devices.
8. [`UserManual.pdf`](customer-support-ai/knowledge_base/UserManual.pdf): User operating guides and troubleshooting steps.

---

## 🧪 Testing & Evaluation

Run unit and integration test suites using `pytest`:

```bash
cd customer-support-ai
pytest backend/tests/ -v
```

Evaluate multi-agent routing accuracy and RAG retrieval precision using the dataset in `datasets/`:

```bash
python backend/scripts/evaluate_agents.py
```

---

## 🚀 Deployment

For production deployment instructions on **Render** (FastAPI backend) and **Vercel** (Next.js frontend), check out the dedicated deployment guide:
👉 [`customer-support-ai/DEPLOYMENT.md`](customer-support-ai/DEPLOYMENT.md)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.


