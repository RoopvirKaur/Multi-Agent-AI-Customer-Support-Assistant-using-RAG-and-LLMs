# System Architecture: Multi-Agent AI Customer Support Assistant

> **Based on:** `Docs/context.md`
> **Generated:** 2026-08-11

---

## Table of Contents

1. [Architecture Philosophy](#1-architecture-philosophy)
2. [High-Level System Diagram](#2-high-level-system-diagram)
3. [Layer-by-Layer Breakdown](#3-layer-by-layer-breakdown)
   - [3.1 Presentation Layer (Frontend)](#31-presentation-layer-frontend)
   - [3.2 API Gateway Layer (Backend)](#32-api-gateway-layer-backend)
   - [3.3 Orchestration Layer](#33-orchestration-layer)
   - [3.4 Agent Layer](#34-agent-layer)
   - [3.5 RAG Layer](#35-rag-layer)
   - [3.6 Memory & Persistence Layer](#36-memory--persistence-layer)
4. [Data Flow Diagrams](#4-data-flow-diagrams)
   - [4.1 Standard Query Flow](#41-standard-query-flow)
   - [4.2 Multi-Agent Routing Flow](#42-multi-agent-routing-flow)
   - [4.3 RAG Pipeline Flow](#43-rag-pipeline-flow)
   - [4.4 Document Ingestion Flow](#44-document-ingestion-flow)
5. [Component Specifications](#5-component-specifications)
   - [5.1 Intent Detection Agent](#51-intent-detection-agent)
   - [5.2 Agent Router](#52-agent-router)
   - [5.3 Specialized Agents](#53-specialized-agents)
   - [5.4 RAG Engine](#54-rag-engine)
   - [5.5 Response Aggregator](#55-response-aggregator)
6. [Database Architecture](#6-database-architecture)
   - [6.1 Relational Database Schema](#61-relational-database-schema)
   - [6.2 Vector Database Design](#62-vector-database-design)
7. [API Architecture](#7-api-architecture)
8. [Security Architecture](#8-security-architecture)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Technology Dependency Map](#10-technology-dependency-map)
11. [Scalability & Extension Points](#11-scalability--extension-points)

---

## 1. Architecture Philosophy

The system is designed around four core principles:

| Principle | Description |
|---|---|
| **Specialization** | Each agent has a focused domain — no agent handles everything |
| **Separation of Concerns** | Routing, retrieval, generation, and memory are independently managed layers |
| **Contextual Grounding** | Every LLM response is anchored to retrieved company documents via RAG |
| **Stateful Conversations** | Session memory ensures continuity across multi-turn interactions |

The architecture follows a **microkernel pattern** at the agent level — a lightweight orchestrator (router) delegates work to pluggable, specialized agents.

---

## 2. High-Level System Diagram

```
+------------------------------------------------------------+
|                        CUSTOMER                            |
+------------------------------------------------------------+
                             |
                    [ HTTP / WebSocket ]
                             |
+------------------------------------------------------------+
|                  PRESENTATION LAYER                        |
|   Next.js / React  |  Tailwind CSS  |  Axios              |
|   - Login/Register page                                    |
|   - Chat Interface (real-time)                             |
|   - Conversation History Panel                             |
|   - (Optional) Analytics Dashboard                        |
+------------------------------------------------------------+
                             |
                    [ REST API calls ]
                             |
+------------------------------------------------------------+
|                  API GATEWAY LAYER                         |
|   Python FastAPI  |  Uvicorn  |  JWT Auth Middleware       |
|                                                            |
|   /api/auth         - Login, Register, Token refresh       |
|   /api/chat         - Send message, get response           |
|   /api/history      - Fetch conversation history           |
|   /api/ingest       - Upload/ingest knowledge base docs    |
|   /api/analytics    - (Optional) Usage metrics             |
+------------------------------------------------------------+
             |                             |
    [Intent + Routing]            [Session Management]
             |                             |
+------------------------+    +----------------------------+
|  ORCHESTRATION LAYER   |    |  MEMORY LAYER              |
|                        |    |                            |
|  Intent Detection      |    |  PostgreSQL / Supabase     |
|  Agent Router          |    |  - sessions table          |
|  Response Aggregator   |    |  - messages table          |
|                        |    |  - users table             |
+------------------------+    +----------------------------+
             |
    [Route to agent(s)]
             |
+--------------------------------------------------------------------+
|                        AGENT LAYER                                 |
|                                                                    |
|  +------------+  +------------+  +----------+  +----------+  +--+ |
|  | Billing    |  | Technical  |  | Product  |  | Complaint|  |FAQ| |
|  | Agent      |  | Agent      |  | Agent    |  | Agent    |  |   | |
|  +-----+------+  +-----+------+  +----+-----+  +----+-----+  +-+-+ |
|        |               |              |              |           |   |
+--------------------------------------------------------------------+
         |               |              |              |           |
         +---------------+--------------+--------------+-----------+
                                        |
                              [Semantic Search Query]
                                        |
+------------------------------------------------------------+
|                     RAG LAYER                              |
|                                                            |
|  Embedding Model (sentence-transformers/all-MiniLM-L6-v2) |
|  Vector Store (FAISS / ChromaDB)                           |
|  Document Retriever (top-k chunks)                         |
+------------------------------------------------------------+
                             |
                   [Retrieved context chunks]
                             |
+------------------------------------------------------------+
|                    LLM LAYER                               |
|   Google Gemini / OpenAI GPT / Llama 3                     |
|   - Per-agent system prompts                               |
|   - Retrieved context injection                            |
|   - Response generation                                    |
+------------------------------------------------------------+
                             |
                   [Generated responses]
                             |
+------------------------------------------------------------+
|                KNOWLEDGE BASE (Storage)                    |
|   PDF Documents: FAQ, Pricing, Refund, Warranty,           |
|                  UserManual, Shipping, Products            |
+------------------------------------------------------------+
```

---

## 3. Layer-by-Layer Breakdown

### 3.1 Presentation Layer (Frontend)

**Technology:** Next.js + React + Tailwind CSS + Axios

```
frontend/
+-- pages/
|   +-- index.tsx            # Landing / login redirect
|   +-- login.tsx            # Login page
|   +-- register.tsx         # Registration page
|   +-- chat.tsx             # Main chat interface
|   +-- dashboard.tsx        # (Optional) Analytics
+-- components/
|   +-- ChatWindow.tsx        # Message list + scroll
|   +-- MessageBubble.tsx     # Individual message display
|   +-- InputBar.tsx          # Message input + send button
|   +-- TypingIndicator.tsx   # AI is thinking animation
|   +-- HistoryPanel.tsx      # Session list sidebar
|   +-- AgentBadge.tsx        # Shows which agent responded
+-- hooks/
|   +-- useChat.ts            # Chat state management
|   +-- useAuth.ts            # Auth state + token handling
+-- services/
|   +-- api.ts                # Axios base config
|   +-- chatService.ts        # Chat API calls
|   +-- authService.ts        # Auth API calls
+-- styles/
    +-- globals.css           # Global Tailwind + custom styles
```

**Key responsibilities:**
- Render real-time chat messages
- Manage JWT tokens in localStorage
- Show which agent(s) handled a query
- Display conversation history per session

---

### 3.2 API Gateway Layer (Backend)

**Technology:** Python FastAPI + Uvicorn + JWT (python-jose)

```
backend/
+-- main.py                   # App entry point, router registration
+-- api/
|   +-- auth.py               # /api/auth routes
|   +-- chat.py               # /api/chat routes
|   +-- history.py            # /api/history routes
|   +-- ingest.py             # /api/ingest routes
+-- middleware/
|   +-- auth_middleware.py    # JWT validation
|   +-- cors_middleware.py    # CORS config
+-- models/
    +-- user.py               # Pydantic user schema
    +-- message.py            # Pydantic message schema
    +-- intent.py             # Pydantic intent schema
```

**Core REST Endpoints:**

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create new user account |
| `POST` | `/api/auth/login` | Authenticate and return JWT |
| `POST` | `/api/auth/refresh` | Refresh expired JWT |
| `POST` | `/api/chat/message` | Send message, get AI response |
| `GET` | `/api/chat/sessions` | List user's chat sessions |
| `GET` | `/api/history/{session_id}` | Get full conversation history |
| `POST` | `/api/ingest/upload` | Upload new knowledge base document |
| `GET` | `/api/analytics/summary` | Get usage statistics (optional) |

---

### 3.3 Orchestration Layer

This is the brain of the system. It coordinates between all components.

```
backend/
+-- agents/
    +-- router.py             # Agent Router
    +-- intent_detector.py    # Intent Detection Agent
    +-- aggregator.py         # Response Aggregator
```

#### Intent Detection Agent (`intent_detector.py`)

- Receives the raw user message
- Calls LLM with a classification prompt
- Returns one or more intent labels from a fixed set

**Intent Categories:**

| Intent Label | Example Query |
|---|---|
| `billing` | "Why was I charged twice this month?" |
| `refund` | "I want a refund for my last order" |
| `technical_support` | "I can't log in to my account" |
| `product` | "What features does the Premium plan include?" |
| `complaint` | "This is unacceptable, I've been waiting 2 weeks" |
| `general_faq` | "What are your support hours?" |

#### Agent Router (`router.py`)

- Receives intent labels from the Intent Detector
- Maps each intent to its responsible agent
- Supports **multi-agent dispatch** (one query → multiple agents)
- Collects all agent responses and passes to Aggregator

**Routing Map:**

```python
ROUTING_MAP = {
    "billing":           BillingAgent,
    "refund":            BillingAgent,    # Refund is a billing sub-domain
    "technical_support": TechnicalAgent,
    "product":           ProductAgent,
    "complaint":         ComplaintAgent,
    "general_faq":       FAQAgent,
}
```

#### Response Aggregator (`aggregator.py`)

- Merges responses from multiple agents into one coherent reply
- Uses LLM to synthesize if multiple agents responded
- Attaches agent metadata (which agent(s) responded)

---

### 3.4 Agent Layer

Each agent is a self-contained Python class with:
- A **system prompt** defining its persona and scope
- A **RAG query** method to retrieve relevant context
- A **generate** method to produce a response via LLM

```
backend/agents/
+-- base_agent.py        # Abstract base class for all agents
+-- billing.py           # Billing Agent
+-- technical.py         # Technical Support Agent
+-- product.py           # Product Agent
+-- complaint.py         # Complaint Agent
+-- faq.py               # FAQ Agent
```

**Base Agent interface:**

```python
class BaseAgent:
    name: str
    system_prompt: str

    def retrieve_context(self, query: str) -> list[str]:
        """Fetch top-k relevant chunks from vector store"""
        ...

    def generate_response(self, query: str, history: list, context: list[str]) -> str:
        """Build prompt and call LLM"""
        ...

    def run(self, query: str, history: list) -> AgentResponse:
        """Orchestrate retrieve -> generate"""
        ...
```

**Agent Responsibility Matrix:**

| Agent | Primary Docs Used | LLM Prompt Focus |
|---|---|---|
| **Billing Agent** | Pricing.pdf, RefundPolicy.pdf | Payment disputes, subscription info, invoice explanation |
| **Technical Agent** | UserManual.pdf, InstallationGuide.pdf | Step-by-step troubleshooting, error resolution |
| **Product Agent** | Products.pdf, Pricing.pdf | Feature comparison, plan differences, availability |
| **Complaint Agent** | FAQ.pdf, RefundPolicy.pdf | Empathetic tone, escalation paths, resolution steps |
| **FAQ Agent** | FAQ.pdf, ShippingPolicy.pdf, Warranty.pdf | Factual policy answers, contact info, general info |

---

### 3.5 RAG Layer

```
backend/
+-- rag/
|   +-- retriever.py          # Semantic search against vector store
|   +-- pipeline.py           # End-to-end RAG orchestration
+-- embeddings/
|   +-- embedder.py           # Wraps sentence-transformers model
+-- vectorstore/
    +-- faiss_store.py        # FAISS index read/write
    +-- chroma_store.py       # ChromaDB alternative
```

**Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- Output: 384-dimensional dense vectors
- Fast, lightweight, effective for semantic similarity

**Retrieval Strategy:**
- Query is embedded into a vector
- Cosine similarity search against FAISS index
- Top-k = 5 chunks returned per query
- Chunks are filtered by relevance threshold (e.g., similarity > 0.75)

**Chunk Configuration:**

| Parameter | Value | Rationale |
|---|---|---|
| Chunk size | 512 tokens | Balances context richness and precision |
| Chunk overlap | 50 tokens | Prevents losing context at boundaries |
| Embedding model | all-MiniLM-L6-v2 | Fast, compact, strong semantic quality |
| Top-k retrieval | 5 chunks | Gives LLM enough context without overload |

---

### 3.6 Memory & Persistence Layer

```
backend/database/
+-- connection.py        # DB connection pool (SQLAlchemy / asyncpg)
+-- models.py            # ORM models (Users, Sessions, Messages)
+-- crud.py              # CRUD helper functions
```

**Conversation Memory Strategy:**

Each API call to `/api/chat/message` includes:
1. Current user message
2. Last N messages from the session (retrieved from DB)
3. This forms the `history` passed to each agent's LLM call

---

## 4. Data Flow Diagrams

### 4.1 Standard Query Flow

```
User types message
       |
       v
[Frontend] POST /api/chat/message
  { user_id, session_id, message }
       |
       v
[FastAPI] Auth middleware validates JWT
       |
       v
[Intent Detector] Classify message intent
  -> Returns: ["billing"]
       |
       v
[Agent Router] Maps intent to BillingAgent
       |
       v
[Billing Agent]
  1. retrieve_context(message)   --> [RAG] top-5 chunks from FAISS
  2. generate_response(message, history, context) --> [Gemini LLM]
  -> Returns: AgentResponse { text, agent_name, source_docs }
       |
       v
[Response Aggregator] Formats single response
       |
       v
[Database] Save (user_msg, ai_response, session_id, timestamp)
       |
       v
[Frontend] Render response with agent badge
```

---

### 4.2 Multi-Agent Routing Flow

```
User: "I paid but Premium is still locked"
       |
       v
[Intent Detector]
  -> Detected intents: ["billing", "technical_support"]
       |
       v
[Agent Router] Dispatch to TWO agents concurrently
       |
       +------------------+
       |                  |
       v                  v
[Billing Agent]     [Technical Agent]
  RAG + LLM           RAG + LLM
  Response A          Response B
       |                  |
       +------------------+
                  |
                  v
    [Response Aggregator]
      LLM merges A + B into single coherent reply
                  |
                  v
         Final Response to User
```

---

### 4.3 RAG Pipeline Flow (Runtime)

```
User Query: "What is your refund policy?"
       |
       v
[Embedder] Encode query -> vector [0.12, -0.34, ... 384 dims]
       |
       v
[FAISS Index] Cosine similarity search
  -> Top-5 matching chunks from knowledge base
       |
       v
[Retrieved Chunks]
  Chunk 1: "Refunds are processed within 5-7 business days..."
  Chunk 2: "To request a refund, navigate to Account > Orders..."
  Chunk 3: "Non-refundable items include digital downloads..."
       |
       v
[LLM Prompt Builder]
  System: "You are the Billing Agent for TechMart Electronics..."
  Context: [Chunk 1, Chunk 2, Chunk 3]
  History: [last 5 messages]
  User: "What is your refund policy?"
       |
       v
[Gemini / GPT] Generate grounded response
       |
       v
"Based on our policy, refunds are processed within 5-7 business days.
 You can request one via Account > Orders. Note that digital downloads
 are non-refundable. Is there anything else I can help you with?"
```

---

### 4.4 Document Ingestion Flow (Offline Pipeline)

```
Admin uploads PDF(s) to knowledge_base/
       |
       v
[PyPDF] Extract raw text from PDF
       |
       v
[Text Splitter] Split into chunks (512 tokens, 50 overlap)
       |
       v
[Embedder] Generate embedding vector per chunk
       |
       v
[FAISS / ChromaDB] Store (vector, chunk_text, metadata)
  Metadata: { source_file, page_number, agent_scope }
       |
       v
Index persisted to disk / cloud storage
```

---

## 5. Component Specifications

### 5.1 Intent Detection Agent

| Property | Detail |
|---|---|
| **Input** | Raw user text message |
| **Output** | List of intent labels (1 to N) |
| **Model** | Google Gemini (zero-shot classification) |
| **Prompt style** | System prompt lists all intents; LLM returns JSON array |
| **Fallback** | Defaults to `general_faq` if classification confidence is low |
| **Multi-label** | Supports returning multiple intents for compound queries |

**Classification Prompt Template:**
```
System: You are an intent classifier for a customer support system.
Classify the user message into one or more of these intents:
[billing, refund, technical_support, product, complaint, general_faq]

Return a JSON array of intents only. Example: ["billing", "technical_support"]

User message: "{user_message}"
```

---

### 5.2 Agent Router

| Property | Detail |
|---|---|
| **Input** | List of intent labels |
| **Output** | List of instantiated agent objects |
| **Dispatch mode** | Parallel async dispatch for multi-agent cases |
| **Error handling** | If an agent fails, others still respond; error is logged |
| **Extensible** | New agents added by registering in ROUTING_MAP |

---

### 5.3 Specialized Agents

#### Billing Agent
- **Scope:** Payments, subscriptions, invoices, refund requests
- **Key docs:** `Pricing.pdf`, `RefundPolicy.pdf`
- **Tone:** Professional, precise, solution-oriented
- **Escalation:** Passes to Complaint Agent if issue unresolvable

#### Technical Support Agent
- **Scope:** Login problems, installation, bugs, error codes
- **Key docs:** `UserManual.pdf`, `InstallationGuide.pdf`
- **Tone:** Patient, step-by-step instructional
- **Escalation:** Flags for human handoff if multi-turn unresolved

#### Product Agent
- **Scope:** Features, plans, pricing, product comparisons
- **Key docs:** `Products.pdf`, `Pricing.pdf`
- **Tone:** Informative, persuasive but honest
- **Escalation:** Routes billing queries to Billing Agent

#### Complaint Agent
- **Scope:** Customer dissatisfaction, escalations, negative sentiment
- **Key docs:** `FAQ.pdf`, `RefundPolicy.pdf`
- **Tone:** Empathetic, de-escalating, apologetic where appropriate
- **Escalation:** Can trigger ticket creation (bonus feature)

#### FAQ Agent
- **Scope:** General policies, hours, contact info, common questions
- **Key docs:** `FAQ.pdf`, `ShippingPolicy.pdf`, `Warranty.pdf`
- **Tone:** Friendly, concise, helpful
- **Escalation:** Defers to specialized agents for domain queries

---

### 5.4 RAG Engine

```
Component          | Technology              | Role
-------------------+-------------------------+-----------------------
Document Loader    | PyPDF                   | Parse PDF files
Text Splitter      | LangChain RecursiveChar | Chunk documents
Embedding Model    | sentence-transformers   | Encode text -> vector
Vector Store       | FAISS                   | Store & search vectors
Retriever          | FAISS similarity search | Fetch top-k chunks
Context Builder    | Custom Python           | Format chunks for LLM
```

---

### 5.5 Response Aggregator

| Scenario | Behavior |
|---|---|
| Single agent responded | Return response as-is with agent badge |
| Multiple agents responded | Use LLM to synthesize into one coherent reply |
| No agent responded | Return fallback: "I'm unable to assist with this, please contact support" |
| Agent error | Log error, return partial response from other agents |

---

## 6. Database Architecture

### 6.1 Relational Database Schema

**Database:** PostgreSQL (via Supabase)

```sql
-- Users table
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name        VARCHAR(255),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Sessions table (one per conversation thread)
CREATE TABLE sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(255),           -- auto-generated from first message
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Messages table (full conversation history)
CREATE TABLE messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role        VARCHAR(10) NOT NULL,   -- 'user' | 'assistant'
    content     TEXT NOT NULL,
    agent_name  VARCHAR(50),            -- which agent responded (nullable)
    intent      VARCHAR(50)[],          -- detected intents (array)
    created_at  TIMESTAMP DEFAULT NOW()
);

-- (Optional) Analytics table
CREATE TABLE analytics_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID REFERENCES sessions(id),
    event_type  VARCHAR(50),            -- 'query', 'escalation', 'satisfaction'
    payload     JSONB,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

**Indexes:**
```sql
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_sessions_user_id    ON sessions(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

---

### 6.2 Vector Database Design

**Technology:** FAISS (flat L2 / cosine similarity index)

```
Vector Store Structure:
+------------------------------------+
| Index: faiss_index.bin             |
| Metadata: faiss_metadata.json      |
+------------------------------------+

Metadata entry per chunk:
{
  "id":          "uuid",
  "text":        "Refunds are processed within...",
  "source_file": "RefundPolicy.pdf",
  "page":        3,
  "agent_scope": ["billing", "complaint"],   // which agents can query this
  "chunk_index": 12
}
```

**Agent-Scoped Retrieval:**
Each agent queries only chunks tagged with its scope. This prevents, for example, the Product Agent from retrieving irrelevant refund policy text.

---

## 7. API Architecture

### Request/Response Contract for `/api/chat/message`

**Request:**
```json
POST /api/chat/message
Authorization: Bearer <jwt_token>

{
  "session_id": "uuid",
  "message": "I paid but Premium is still locked"
}
```

**Response:**
```json
{
  "message_id": "uuid",
  "response": "We're sorry to hear about this issue...",
  "agents_invoked": ["billing", "technical_support"],
  "intent": ["billing", "technical_support"],
  "session_id": "uuid",
  "timestamp": "2026-08-11T14:48:00Z",
  "sources": [
    { "document": "Pricing.pdf", "page": 2 },
    { "document": "UserManual.pdf", "page": 7 }
  ]
}
```

### Authentication Flow

```
Client             FastAPI              PostgreSQL
   |                  |                    |
   |-- POST /login --> |                   |
   |                  |-- SELECT user --> |
   |                  |<-- user record -- |
   |                  |-- validate hash   |
   |<-- JWT token ---- |                  |
   |                  |                   |
   |-- POST /chat --> |                   |
   |  (Bearer token)  |                   |
   |                  |-- verify JWT      |
   |                  |-- process query   |
   |<-- AI response -- |                  |
```

---

## 8. Security Architecture

| Concern | Mechanism |
|---|---|
| **Authentication** | JWT tokens (HS256), 24h expiry with refresh |
| **Password storage** | bcrypt hashing (min cost factor 12) |
| **API protection** | All `/api/chat` and `/api/history` routes require valid JWT |
| **CORS** | Whitelist only frontend domain |
| **Input validation** | Pydantic schemas enforce type and length on all inputs |
| **Rate limiting** | Limit to 30 requests/minute per user (FastAPI middleware) |
| **LLM prompt injection** | System prompt is always pre-pended before user input |
| **Secrets management** | API keys in environment variables, never hardcoded |

---

## 9. Deployment Architecture

```
+-------------------+      +-------------------+      +-------------------+
|    VERCEL         |      |   RAILWAY / RENDER|      |  SUPABASE         |
|                   |      |                   |      |                   |
|  Next.js Frontend |----->|  FastAPI Backend   |----->| PostgreSQL DB     |
|  (CDN edge)       |      |  (Docker container)|      | (managed cloud)  |
+-------------------+      +-------------------+      +-------------------+
                                    |
                           +--------+--------+
                           |                 |
                  +--------v------+  +-------v-------+
                  | FAISS Index   |  | Cloud Storage |
                  | (local to     |  | (PDFs /       |
                  |  container)   |  |  knowledge    |
                  +---------------+  |  base)        |
                                     +---------------+
```

**Environment Variables required by backend:**

```env
# LLM
GEMINI_API_KEY=your_gemini_api_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Auth
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Store
FAISS_INDEX_PATH=./vectorstore/faiss_index.bin
FAISS_METADATA_PATH=./vectorstore/faiss_metadata.json
```

---

## 10. Technology Dependency Map

```
Frontend (Next.js)
    |-- Axios            -> HTTP calls to FastAPI
    |-- React Context    -> Auth state management
    |-- Tailwind CSS     -> Styling
    |-- WebSocket (opt.) -> Real-time streaming responses

Backend (FastAPI)
    |-- LangChain        -> Agent prompt management, RAG chains
    |-- LangGraph (opt.) -> Complex multi-agent state machines
    |-- sentence-transformers -> Embedding generation
    |-- FAISS            -> Vector similarity search
    |-- PyPDF            -> PDF text extraction
    |-- SQLAlchemy       -> ORM for PostgreSQL
    |-- python-jose      -> JWT token handling
    |-- bcrypt           -> Password hashing
    |-- Uvicorn          -> ASGI server

External Services
    |-- Google Gemini API -> LLM inference
    |-- Supabase          -> Managed PostgreSQL
    |-- Vercel            -> Frontend hosting + CDN
    |-- Railway / Render  -> Backend hosting
```

---

## 11. Scalability & Extension Points

### Current Scalability

| Bottleneck | Solution |
|---|---|
| Single FAISS index (in-memory) | Replace with Pinecone (cloud vector DB) for scale |
| Synchronous agent calls | Use `asyncio.gather()` for parallel multi-agent dispatch |
| Single backend instance | Deploy behind a load balancer on Railway |

### Extension Points (Bonus Features)

| Feature | Where to Add |
|---|---|
| **Sentiment Analysis** | Add pre-processing step in Orchestration Layer before routing |
| **Voice Support** | Add WebSpeech API on frontend; Speech-to-Text before intent detection |
| **Multilingual** | Add language detection; route through translation before/after LLM |
| **Ticket Creation** | Complaint Agent triggers a POST to ticketing API (e.g., Zendesk) |
| **Human Handoff** | Complaint Agent sets `escalate: true`; frontend opens live chat widget |
| **Email/WhatsApp** | Add Twilio / SendGrid webhook endpoints as new API routes |
| **Admin Dashboard** | New `/admin` pages in frontend; new `/api/admin` routes in backend |
| **Streaming Responses** | Replace REST response with Server-Sent Events (SSE) in FastAPI |

---

> **Architecture version:** 1.0
> **Last updated:** 2026-08-11
> **Next review:** Update after Phase 4 (AI Agent Development) is complete
