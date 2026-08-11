# 🤖 Multi-Agent AI Customer Support Assistant

A production-ready, multi-agent customer support system powered by **Google Gemini**, **FastAPI**, **Next.js**, and **FAISS** vector search. Built for **TechMart Electronics** as a demonstration of agentic AI orchestration.

## 📐 Architecture Overview

```
User Query
    │
    ▼
Intent Detection Agent (Gemini)
    │  Detects: billing | technical | product | complaint | faq
    ▼
Agent Router
    │  Routes to one or more specialized agents (parallel)
    ├──► Billing Agent
    ├──► Technical Support Agent
    ├──► Product Agent
    ├──► Complaint Agent
    └──► FAQ Agent
              │
              ▼
         RAG Retrieval (FAISS + sentence-transformers)
              │
              ▼
         Gemini LLM (grounded response)
              │
              ▼
         Response Aggregator
              │
              ▼
         Final Response to User
```

## 🗂️ Project Structure

```
customer-support-ai/
├── frontend/           # Next.js 14 app (TypeScript + Tailwind)
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

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

Run the DDL script in your Supabase SQL Editor (see `Docs/implementation_plan.md` Phase 1 for the full DDL).

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

## 🔑 Environment Variables

See [`.env.example`](.env.example) for the full list of required variables.

## 🤖 Agents

| Agent | Scope | Handles |
|---|---|---|
| Billing Agent | `billing` | Payments, invoices, refunds, subscriptions |
| Technical Support Agent | `technical` | Installation, bugs, errors, password reset |
| Product Agent | `product` | Features, plans, pricing, availability |
| Complaint Agent | `complaint` | Dissatisfaction, escalation, unresolved issues |
| FAQ Agent | `faq` | Policies, hours, contact info, general queries |

## 📚 Knowledge Base

8 documents covering TechMart Electronics policies, products, and support:
- `FAQ.pdf`, `RefundPolicy.pdf`, `ShippingPolicy.pdf`, `Warranty.pdf`
- `Pricing.pdf`, `Products.pdf`, `InstallationGuide.pdf`, `UserManual.pdf`

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11, Uvicorn |
| Database | PostgreSQL (Supabase), SQLAlchemy (async) |
| AI / LLM | Google Gemini via `langchain-google-genai` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Store | FAISS (CPU) |
| Auth | JWT (HS256) with bcrypt password hashing |
| Rate Limiting | SlowAPI |

## 📄 License

MIT
