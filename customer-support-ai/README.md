# 🤖 Multi-Agent AI Customer Support Assistant (TechMart Electronics)

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Pro%2FFlash-4285F4.svg)](https://aistudio.google.com/)
[![FAISS](https://img.shields.io/badge/VectorStore-FAISS-orange.svg)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready, autonomous multi-agent customer support system built for **TechMart Electronics**. Powered by **Google Gemini**, **FastAPI**, **Next.js 14**, and **FAISS** vector search.

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

## 🗂️ Project Structure

```
customer-support-ai/
├── frontend/           # Next.js 14 app (TypeScript + Tailwind CSS)
├── backend/
│   ├── agents/         # Specialized AI agents + router + aggregator
│   ├── api/            # FastAPI route handlers
│   ├── database/       # SQLAlchemy models + CRUD helpers
│   ├── embeddings/     # Sentence-transformer embedder
│   ├── llm/            # Gemini LLM client
│   ├── middleware/     # Auth + CORS middleware
│   ├── models/         # Pydantic schemas
│   ├── rag/            # RAG pipeline + retriever
│   ├── scripts/        # CLI utilities (ingest, seed)
│   └── vectorstore/    # FAISS index + metadata
├── knowledge_base/     # Source PDFs for TechMart Electronics
├── datasets/           # Sample datasets for testing
├── .env.example        # Environment variable template
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 🚀 Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Supabase](https://supabase.com) project (PostgreSQL)
- A [Google AI Studio](https://aistudio.google.com/app/api-keys) Gemini API key

### 1. Clone & Configure Environment

```bash
git clone <your-repo-url>
cd customer-support-ai
cp .env.example .env
# Fill in your real values in .env
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

Run the DDL script in your Supabase SQL Editor (see `Docs/architecture.md` for full database schema).

### 4. Ingest Knowledge Base

```bash
python backend/scripts/ingest_documents.py
```

### 5. Run Backend

```bash
uvicorn backend.main:app --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 6. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# App available at http://localhost:3000
```

---

## 🔑 Environment Variables

See [`.env.example`](.env.example) for the full list of required variables.

---

## 🤖 Specialized Agents

| Agent | Scope | Description / Handles |
|---|---|---|
| **Billing Agent** | `billing` | Payments, invoices, refunds, subscriptions, transaction errors |
| **Technical Support Agent** | `technical` | Installation, device bugs, errors, firmware, connectivity |
| **Product Agent** | `product` | Specifications, pricing tiers, feature comparison, availability |
| **Complaint Agent** | `complaint` | Dissatisfaction, escalations, apology messaging, priority tickets |
| **FAQ Agent** | `faq` | Store hours, shipping options, warranty policies, general questions |

---

## 📚 Knowledge Base

8 PDF documents covering TechMart Electronics policies and product manuals:
- `FAQ.pdf`, `RefundPolicy.pdf`, `ShippingPolicy.pdf`, `Warranty.pdf`
- `Pricing.pdf`, `Products.pdf`, `InstallationGuide.pdf`, `UserManual.pdf`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.11, Uvicorn |
| **Database** | PostgreSQL (Supabase), SQLAlchemy (async) |
| **AI / LLM** | Google Gemini via `langchain-google-genai` |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector Store** | FAISS (CPU) |
| **Auth** | JWT (HS256) with bcrypt password hashing |
| **Rate Limiting** | SlowAPI |

---

## 📄 License

MIT

