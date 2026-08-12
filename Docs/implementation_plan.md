# Phase-Wise Implementation Plan
## Multi-Agent AI Customer Support Assistant

> **Based on:** `Docs/architecture.md`
> **Generated:** 2026-08-11
> **Total Phases:** 8 | **Estimated Duration:** ~8–10 weeks

---

## Overview

```
Phase 0  -->  Phase 1  -->  Phase 2  -->  Phase 3  -->  Phase 4
(Setup)      (Database)    (Backend     (Auth &      (AI Agents &
                            Core API)    Frontend)    Orchestration)
                                                           |
Phase 8  <--  Phase 7  <--  Phase 6  <--  Phase 5  <-------+
(Bonus)      (Deployment)  (Testing)     (RAG Pipeline)
```

---

## Dependency Order

```
Phase 0 (Setup)
    |
    +--> Phase 1 (DB Schema)
    |        |
    |        +--> Phase 2 (Backend Core API + Auth)
    |                 |
    |                 +--> Phase 3 (Frontend)
    |                 |
    |                 +--> Phase 4 (RAG Pipeline)
    |                           |
    |                           +--> Phase 5 (AI Agents)
    |                                     |
    |                                     +--> Phase 6 (Integration & Testing)
    |                                               |
    |                                               +--> Phase 7 (Deployment)
    |                                                         |
    |                                                         +--> Phase 8 (Bonus)
```

---

## Phase 0 — Project Setup & Infrastructure

> **Goal:** Establish the project skeleton, toolchain, and external service accounts before any code is written.

### 0.1 Repository & Tooling

- [x] Initialize Git repository with `main` and `dev` branches
- [x] Create root `README.md` with project description
- [x] Add `.gitignore` (Python, Node, `.env` files)
- [x] Create `requirements.txt` (backend) and `package.json` (frontend) stubs

**Folder scaffold to create:**
```
customer-support-ai/
+-- frontend/
+-- backend/
|   +-- agents/
|   +-- api/
|   +-- database/
|   +-- embeddings/
|   +-- middleware/
|   +-- models/
|   +-- rag/
|   +-- vectorstore/
+-- knowledge_base/
+-- datasets/
+-- .env.example
+-- requirements.txt
+-- README.md
```

### 0.2 External Service Accounts

- [x] Create **Supabase** project → note `DATABASE_URL` (Configured in `.env`)
- [x] Create **Google Gemini API** key → note `GEMINI_API_KEY` (Configured in `.env`)
- [x] Create **Vercel** account (linked to GitHub repo)
- [x] Create **Railway** or **Render** account

### 0.3 Environment Configuration

Create `.env.example` with all required keys (no real values):
```env
GEMINI_API_KEY=
DATABASE_URL=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_INDEX_PATH=./vectorstore/faiss_index.bin
FAISS_METADATA_PATH=./vectorstore/faiss_metadata.json
FRONTEND_URL=http://localhost:3000
```

### 0.4 Python Environment

- [x] Create Python virtual environment (`python -m venv venv`)
- [x] Install base backend dependencies:

```
fastapi
uvicorn[standard]
python-jose[cryptography]
passlib[bcrypt]
sqlalchemy
asyncpg
pydantic
python-dotenv
langchain
langchain-community
langchain-google-genai
faiss-cpu
sentence-transformers
pypdf
pandas
```

### 0.5 Node.js Environment

- [x] Scaffold Next.js frontend:
```bash
npx create-next-app@latest frontend --typescript --tailwind --app
```
- [x] Install additional frontend packages:
```bash
npm install axios react-markdown lucide-react
```

**Deliverable at end of Phase 0:**
- Repo initialized, folder structure created, all accounts set up, `.env` configured locally, both environments installable without errors.

---

## Phase 1 — Database Design & Setup

> **Goal:** Create the PostgreSQL schema in Supabase and set up ORM models.

### 1.1 Supabase Project Initialization

- [ ] Log in to Supabase and open the SQL editor
- [ ] Run the schema creation script:

**Tables to create:**

| Table | Purpose |
|---|---|
| `users` | Stores registered user accounts |
| `sessions` | One record per conversation thread |
| `messages` | Full message history (user + assistant turns) |
| `analytics_events` | Optional: usage and escalation events |

**Full DDL:**
```sql
-- users
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name          VARCHAR(255),
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);

-- sessions
CREATE TABLE sessions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    title      VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- messages
CREATE TABLE messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role       VARCHAR(10) NOT NULL,    -- 'user' | 'assistant'
    content    TEXT NOT NULL,
    agent_name VARCHAR(50),
    intent     VARCHAR(50)[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- analytics_events (optional)
CREATE TABLE analytics_events (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    event_type VARCHAR(50),
    payload    JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_sessions_user_id    ON sessions(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

### 1.2 SQLAlchemy ORM Models

- [ ] Create `backend/database/connection.py` — async engine + session factory
- [ ] Create `backend/database/models.py` — ORM classes mirroring SQL schema
- [ ] Create `backend/database/crud.py` — helper functions:
  - `create_user()`, `get_user_by_email()`
  - `create_session()`, `get_sessions_by_user()`
  - `save_message()`, `get_messages_by_session()`

### 1.3 Verification

- [ ] Run a test script to connect to Supabase and insert/retrieve a test row
- [ ] Confirm all indexes exist in Supabase dashboard

**Deliverable:** Supabase schema live, ORM models defined, CRUD helpers tested.

---

## Phase 2 — Backend Core API

> **Goal:** Build the FastAPI server with authentication, middleware, and all REST endpoints (returning stubs initially).

### 2.1 FastAPI App Entry Point

- [ ] Create `backend/main.py`:
  - Register all routers (`/api/auth`, `/api/chat`, `/api/history`, `/api/ingest`)
  - Configure CORS middleware (allow `FRONTEND_URL`)
  - Add lifespan handler to initialize DB connection on startup

### 2.2 Pydantic Schemas

- [ ] `backend/models/user.py` — `UserCreate`, `UserLogin`, `UserOut`
- [ ] `backend/models/message.py` — `MessageIn`, `MessageOut`, `ChatResponse`
- [ ] `backend/models/intent.py` — `IntentLabel`, `IntentResponse`

### 2.3 Authentication Module

- [ ] Create `backend/api/auth.py`:
  - `POST /api/auth/register` — hash password with bcrypt, insert into `users`
  - `POST /api/auth/login` — verify bcrypt hash, return signed JWT (HS256)
  - `POST /api/auth/refresh` — verify old token, issue new token
- [ ] Create `backend/middleware/auth_middleware.py`:
  - FastAPI `Depends()` function that extracts and validates Bearer JWT
  - Returns `user_id` for use in protected routes

### 2.4 Chat API (Stub)

- [ ] Create `backend/api/chat.py`:
  - `POST /api/chat/message` — accepts `{ session_id, message }`, returns stub response `{ response: "Working...", agents_invoked: [] }`
  - `GET /api/chat/sessions` — returns list of sessions for authenticated user

### 2.5 History API

- [ ] Create `backend/api/history.py`:
  - `GET /api/history/{session_id}` — returns all messages for a session (authenticated)

### 2.6 Ingest API (Stub)

- [ ] Create `backend/api/ingest.py`:
  - `POST /api/ingest/upload` — accepts PDF file upload, returns `{ status: "received" }` (full pipeline wired in Phase 4)

### 2.7 Middleware

- [ ] `backend/middleware/cors_middleware.py` — CORS config
- [ ] Rate limiting: add `slowapi` for 30 requests/min per user

### 2.8 Verification

- [ ] Run `uvicorn backend.main:app --reload`
- [ ] Test all endpoints using Swagger UI (`http://localhost:8000/docs`)
- [ ] Verify register → login → get JWT → access protected route works end-to-end

**Deliverable:** Fully working auth flow, all API routes registered and responding, Swagger docs available.

---

## Phase 3 — Frontend Development

> **Goal:** Build the complete Next.js frontend — login, register, chat interface, and conversation history panel.

### 3.1 Global Styles & Design System

- [ ] Configure `tailwind.config.ts` with custom color palette and fonts
- [ ] Set up `globals.css` with CSS variables for theming
- [ ] Install and configure Google Font (e.g., Inter)

### 3.2 Auth Service & Hooks

- [ ] `frontend/services/api.ts` — Axios instance with `baseURL` and JWT interceptor
- [ ] `frontend/services/authService.ts` — `login()`, `register()`, `logout()`, `refreshToken()`
- [ ] `frontend/hooks/useAuth.ts` — React Context for auth state; stores JWT in `localStorage`

### 3.3 Pages

#### Login Page (`pages/login.tsx`)
- [ ] Email + password form
- [ ] Submit calls `authService.login()`, stores JWT, redirects to `/chat`
- [ ] Link to Register page

#### Register Page (`pages/register.tsx`)
- [ ] Name + email + password form
- [ ] Submit calls `authService.register()`, auto-login on success

#### Chat Page (`pages/chat.tsx`) — **Core page**
- [ ] Protected route (redirect to `/login` if no JWT)
- [ ] Layout: left sidebar (session list) + main chat area
- [ ] On load: fetch and display user's sessions via `GET /api/chat/sessions`
- [ ] Start new session button

### 3.4 Components

| Component | File | Responsibility |
|---|---|---|
| ChatWindow | `ChatWindow.tsx` | Scrollable message list, auto-scroll to bottom |
| MessageBubble | `MessageBubble.tsx` | User vs assistant styling, timestamp, agent badge |
| AgentBadge | `AgentBadge.tsx` | Colored pill showing which agent(s) responded |
| InputBar | `InputBar.tsx` | Textarea + send button; Enter to send, Shift+Enter for newline |
| TypingIndicator | `TypingIndicator.tsx` | Animated dots while waiting for API response |
| HistoryPanel | `HistoryPanel.tsx` | Session list; click to load a session |

### 3.5 Chat Service & Hook

- [ ] `frontend/services/chatService.ts` — `sendMessage()`, `getSessions()`, `getHistory()`
- [ ] `frontend/hooks/useChat.ts` — manages messages state, loading state, session state

### 3.6 Connect Frontend to Backend

- [ ] Wire `sendMessage()` to `POST /api/chat/message` (will return stub response in this phase)
- [ ] Wire session list to `GET /api/chat/sessions`
- [ ] Wire history load to `GET /api/history/{session_id}`

### 3.7 Verification

- [ ] Navigate register → login → chat flow without errors
- [ ] Sending a message shows the stub response with typing indicator
- [ ] Sessions appear in sidebar and history loads on click

**Deliverable:** Fully functional frontend UI connected to the backend, auth flow working, chat UI rendering stub responses.

---

## Phase 4 — RAG Pipeline

> **Goal:** Build the document ingestion pipeline and runtime retrieval system that all agents will use.

### 4.1 Knowledge Base Documents

- [ ] Create the fictional company: **TechMart Electronics**
- [ ] Author and save the following PDFs into `knowledge_base/`:

| File | Content to include |
|---|---|
| `FAQ.pdf` | Top 20 common questions about TechMart products and services |
| `RefundPolicy.pdf` | Refund window (30 days), non-refundable items, process steps |
| `ShippingPolicy.pdf` | Delivery times, shipping costs, tracking, international shipping |
| `Warranty.pdf` | 1-year warranty terms, what's covered, how to claim |
| `Pricing.pdf` | All product tiers, subscription plans, discount policies |
| `Products.pdf` | Product catalog with specs, features, and availability |
| `InstallationGuide.pdf` | Step-by-step setup guide for top 3 TechMart products |
| `UserManual.pdf` | Full user manual with troubleshooting section |

### 4.2 Embedder Module

- [ ] Create `backend/embeddings/embedder.py`:
  - Load `sentence-transformers/all-MiniLM-L6-v2`
  - `encode(text: str) -> np.ndarray` — returns 384-dim vector
  - `encode_batch(texts: list[str]) -> np.ndarray` — batch encoding

### 4.3 Document Ingestion Pipeline

- [ ] Create `backend/rag/pipeline.py`:
  - `load_pdf(path: str) -> str` — using PyPDF
  - `split_into_chunks(text: str, chunk_size=512, overlap=50) -> list[str]` — LangChain `RecursiveCharacterTextSplitter`
  - `assign_agent_scope(source_file: str) -> list[str]` — maps file to agent scopes

**Agent-scope mapping:**
```python
SCOPE_MAP = {
    "faq.pdf":              ["faq", "complaint"],
    "refund_policy.pdf":    ["billing", "complaint"],
    "shipping_policy.pdf":  ["faq", "billing"],
    "warranty.pdf":         ["faq", "technical"],
    "pricing.pdf":          ["billing", "product"],
    "products.pdf":         ["product"],
    "installation_guide.pdf": ["technical"],
    "user_manual.pdf":      ["technical"],
}
```

### 4.4 Vector Store Module

- [ ] Create `backend/vectorstore/faiss_store.py`:
  - `build_index(embeddings: np.ndarray) -> faiss.Index`
  - `save_index(index, path)` / `load_index(path)`
  - `save_metadata(metadata: list[dict], path)` / `load_metadata(path)`

### 4.5 Retriever Module

- [ ] Create `backend/rag/retriever.py`:
  - `retrieve(query: str, agent_scope: str, top_k=5) -> list[dict]`
  - Embeds query, searches FAISS, filters by `agent_scope`, returns top-k chunks with metadata

### 4.6 Ingest Script & API

- [ ] Create `backend/scripts/ingest_documents.py` — offline CLI script to process all PDFs in `knowledge_base/` and build the FAISS index
- [ ] Wire `POST /api/ingest/upload` to accept a PDF file and run the ingestion pipeline, appending to the existing index

### 4.7 Verification

- [ ] Run `python backend/scripts/ingest_documents.py`
- [ ] Confirm `faiss_index.bin` and `faiss_metadata.json` are created
- [ ] Write a quick test: query "what is your refund policy?" and inspect top-5 chunks returned

**Deliverable:** All 8 PDFs ingested, FAISS index built, retriever returning semantically correct chunks for test queries.

---

## Phase 5 — AI Agents & Orchestration

> **Goal:** Build all 5 specialized agents, the intent detector, agent router, and response aggregator. Connect them to the RAG layer and LLM.

### 5.1 LLM Client Setup

- [ ] Create `backend/llm/gemini_client.py`:
  - Wrap `google-generativeai` SDK
  - `generate(system_prompt: str, history: list, context: list[str], user_message: str) -> str`
  - Handle API errors and retries gracefully

### 5.2 Base Agent

- [ ] Create `backend/agents/base_agent.py`:
```python
class BaseAgent:
    name: str
    system_prompt: str
    agent_scope: str

    def retrieve_context(self, query: str) -> list[str]: ...
    def generate_response(self, query: str, history: list, context: list[str]) -> str: ...
    def run(self, query: str, history: list) -> AgentResponse: ...
```

### 5.3 Specialized Agents

For each agent, implement `system_prompt`, `agent_scope`, and inherit `BaseAgent`:

#### 5.3.1 Billing Agent (`backend/agents/billing.py`)
- [ ] `agent_scope = "billing"`
- [ ] System prompt: professional, payment-focused persona for TechMart Electronics
- [ ] Handle: payment issues, subscription queries, invoice questions, refund requests

#### 5.3.2 Technical Support Agent (`backend/agents/technical.py`)
- [ ] `agent_scope = "technical"`
- [ ] System prompt: patient, instructional persona; references UserManual and InstallationGuide
- [ ] Handle: login issues, password reset, installation steps, bug reports, error codes

#### 5.3.3 Product Agent (`backend/agents/product.py`)
- [ ] `agent_scope = "product"`
- [ ] System prompt: informative product expert; references Products.pdf and Pricing.pdf
- [ ] Handle: feature questions, plan comparisons, product availability

#### 5.3.4 Complaint Agent (`backend/agents/complaint.py`)
- [ ] `agent_scope = "complaint"`
- [ ] System prompt: empathetic, de-escalating persona; apologetic tone
- [ ] Handle: dissatisfaction, escalation requests, unresolved issues

#### 5.3.5 FAQ Agent (`backend/agents/faq.py`)
- [ ] `agent_scope = "faq"`
- [ ] System prompt: friendly, concise; references FAQ, Shipping, Warranty docs
- [ ] Handle: policy questions, hours, contact info, general queries

### 5.4 Intent Detection Agent

- [ ] Create `backend/agents/intent_detector.py`:
  - Use Gemini with the classification prompt from architecture:
    ```
    System: You are an intent classifier...
    Return a JSON array: ["billing", "technical_support"]
    ```
  - Parse JSON response safely (fallback to `["general_faq"]` on failure)
  - Return `list[str]` of detected intents

### 5.5 Agent Router

- [ ] Create `backend/agents/router.py`:
  - `ROUTING_MAP` dict mapping intent → agent class
  - `route(intents: list[str]) -> list[BaseAgent]` — deduplicate agents
  - `dispatch_all(agents, query, history) -> list[AgentResponse]` — use `asyncio.gather()` for parallel execution

### 5.6 Response Aggregator

- [ ] Create `backend/agents/aggregator.py`:

| Scenario | Logic |
|---|---|
| 1 agent response | Return as-is |
| 2+ agent responses | Call Gemini to synthesize into one coherent reply |
| 0 responses / all errors | Return hardcoded fallback message |

### 5.7 Wire Agents into Chat API

- [ ] Update `backend/api/chat.py` `POST /api/chat/message`:
  1. Retrieve last 10 messages from DB (`crud.get_messages_by_session()`)
  2. Call `intent_detector.detect(message)`
  3. Call `router.route(intents)` → get agents
  4. Call `router.dispatch_all(agents, message, history)` → responses
  5. Call `aggregator.aggregate(responses)` → final reply
  6. Save user message + AI response to DB
  7. Return `ChatResponse` with full metadata

### 5.8 Verification

- [ ] Test with single-intent queries (e.g., "What is your refund policy?")
  - Expect: BillingAgent responds with RAG-grounded answer
- [ ] Test with multi-intent queries (e.g., "I paid but can't log in")
  - Expect: Both BillingAgent and TechnicalAgent respond; aggregator merges
- [ ] Test fallback: send an unrelated query
  - Expect: FAQAgent responds or fallback message returned

**Deliverable:** All 5 agents functional, intent detection accurate, multi-agent routing working, RAG-grounded responses generated by Gemini.

---

## Phase 6 — Integration & Testing

> **Goal:** Connect all layers end-to-end, validate correctness, and fix integration issues.

### 6.1 End-to-End Integration Tests

- [ ] **Auth flow:** Register → Login → Get JWT → Access `/api/chat/message`
- [ ] **New session creation:** First message auto-creates a session
- [ ] **Conversation history:** Second message in session has access to first message context
- [ ] **History page:** Reload chat; history panel shows past sessions and messages load correctly

### 6.2 Agent Routing Tests

Test the following query scenarios and verify correct agent dispatch:

| Query | Expected Agent(s) |
|---|---|
| "Can I get a refund?" | Billing Agent |
| "I can't install the app" | Technical Support Agent |
| "What's included in the Pro plan?" | Product Agent |
| "I'm very unhappy with your service" | Complaint Agent |
| "What are your business hours?" | FAQ Agent |
| "I paid but Premium is locked" | Billing + Technical |
| "The product broke and I want a refund" | Billing + Complaint |

### 6.3 RAG Quality Evaluation

For each agent, test 5 sample queries and verify:
- [ ] Retrieved chunks are semantically relevant
- [ ] LLM response references content from the chunks
- [ ] Source documents are correctly attributed in response metadata

### 6.4 Edge Cases

- [ ] Empty message submitted → validation error returned
- [ ] Very long message (> 4000 chars) → truncation or error handled
- [ ] Invalid session ID → 404 returned
- [ ] Expired JWT → 401 returned with clear message
- [ ] FAISS index file missing → graceful error, not 500

### 6.5 Performance Baseline

- [ ] Measure average response time per query (target: < 5 seconds)
- [ ] Measure response time for multi-agent queries
- [ ] Log slow queries (> 8 seconds) for optimization

### 6.6 Security Checklist

- [ ] Confirm all `/api/chat` routes reject requests without JWT
- [ ] Confirm users cannot access another user's session history
- [ ] Confirm `.env` file is not committed to Git
- [ ] Confirm Pydantic validation rejects malformed inputs

**Deliverable:** All integration tests passing, edge cases handled, response times within target, security checks complete.

---

## Phase 7 — Deployment

> **Goal:** Deploy frontend to Vercel, backend to Railway/Render, and connect all services.

### 7.1 Backend Deployment (Railway / Render)

- [ ] Create `Dockerfile` for the FastAPI backend:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- [ ] Push to Railway/Render; configure environment variables in the dashboard:
  - `GEMINI_API_KEY`, `DATABASE_URL`, `JWT_SECRET_KEY`, etc.
- [ ] Run the ingest script on the deployed container to build the FAISS index
- [ ] Note the deployed backend URL (e.g., `https://my-api.railway.app`)

### 7.2 Frontend Deployment (Vercel)

- [ ] Set `NEXT_PUBLIC_API_URL` to the deployed backend URL
- [ ] Connect GitHub repo to Vercel
- [ ] Push to `main` branch → Vercel auto-deploys
- [ ] Verify deployed frontend URL (e.g., `https://my-app.vercel.app`)

### 7.3 CORS Update

- [ ] Update backend `CORS_ORIGINS` environment variable to include the Vercel production URL
- [ ] Redeploy backend

### 7.4 End-to-End Production Test

- [ ] Register and login on the production URL
- [ ] Send one query per agent domain and verify correct responses
- [ ] Verify conversation history persists across browser refresh
- [ ] Verify the FAISS index loads correctly from the deployed container

### 7.5 Monitoring & Logs

- [ ] Enable Railway/Render log streaming
- [ ] Add structured logging (`loguru` or Python `logging`) to all agent runs
- [ ] Log: query, intent detected, agents invoked, response time, errors

**Deliverable:** Application live at production URLs, all features working in production, logs accessible.

---

## Phase 8 — Bonus Enhancements (Optional)

> **Goal:** Implement selected bonus features to exceed baseline requirements.

Choose any of the following based on remaining time:

### 8.1 Sentiment Analysis Pre-Routing
- [ ] Add a pre-processing step in the orchestration layer
- [ ] If sentiment is highly negative → always include `ComplaintAgent`
- [ ] Use Gemini or a lightweight classifier for sentiment scoring

### 8.2 Streaming Responses (SSE)
- [ ] Replace `POST /api/chat/message` standard JSON response with Server-Sent Events
- [ ] Stream Gemini tokens to frontend as they are generated
- [ ] Frontend renders tokens progressively in `ChatWindow`

### 8.3 Analytics Dashboard
- [ ] Create `backend/api/analytics.py`: `GET /api/analytics/summary`
  - Total conversations, agent usage counts, avg response time
- [ ] Create `frontend/pages/dashboard.tsx` with charts (use `recharts` or `chart.js`)

### 8.4 Admin Knowledge Base Management
- [ ] Create `frontend/pages/admin.tsx` — upload new PDFs, list existing docs
- [ ] Wire to `POST /api/ingest/upload` to add new docs and re-index

### 8.5 Human Handoff Flag
- [ ] `ComplaintAgent` sets `escalate: true` in `AgentResponse` when unresolvable
- [ ] Frontend shows a "Connect to Human Agent" button when `escalate: true`

### 8.6 Automatic Ticket Creation
- [ ] When `ComplaintAgent` escalates, trigger a POST to a mock ticketing API
- [ ] Return ticket ID in response; display to user

---

## Deliverables Checklist

| # | Deliverable | Phase |
|---|---|---|
| 1 | Source code (frontend + backend) on GitHub | Phase 0–7 |
| 2 | `README.md` with local setup instructions | Phase 0 |
| 3 | `.env.example` with all required keys documented | Phase 0 |
| 4 | PostgreSQL schema DDL | Phase 1 |
| 5 | Knowledge base PDFs (8 documents) | Phase 4 |
| 6 | FAISS index built from ingested PDFs | Phase 4 |
| 7 | All 5 specialized agents + intent detector + router | Phase 5 |
| 8 | Deployed frontend URL (Vercel) | Phase 7 |
| 9 | Deployed backend URL (Railway/Render) | Phase 7 |
| 10 | Demonstration video (compulsory) | Phase 7 |
| 11 | Project report (PDF) | Phase 7 |

---

## Recommended Weekly Schedule

| Week | Phases |
|---|---|
| Week 1 | Phase 0 (Setup) + Phase 1 (Database) |
| Week 2 | Phase 2 (Backend Core API) |
| Week 3 | Phase 3 (Frontend) |
| Week 4 | Phase 4 (RAG Pipeline) |
| Week 5–6 | Phase 5 (AI Agents & Orchestration) |
| Week 7 | Phase 6 (Integration & Testing) |
| Week 8 | Phase 7 (Deployment) + Demo Video |
| Week 9–10 | Phase 8 (Bonus features, if time allows) |

---

> **Plan version:** 1.0
> **Last updated:** 2026-08-11
> **Reference architecture:** `Docs/architecture.md`
