# Project Context: Multi-Agent AI Customer Support Assistant

> **Source:** `Docs/ProblemStatement.txt`  
> **Generated:** 2026-08-11

---

## 1. Project Overview

**Title:** Multi-Agent AI Customer Support Assistant using RAG and LLMs

**Goal:** Build a web-based AI-powered customer support system that intelligently handles customer queries by routing them to specialized AI agents, retrieving relevant knowledge, and generating accurate, context-aware responses.

### Core Capabilities
- Understand customer **intent**
- **Route** requests to the correct specialized agent
- **Retrieve** relevant company information via RAG
- **Generate** accurate LLM responses
- **Maintain** conversation history across sessions
- **Escalate** unresolved issues

---

## 2. Problem Being Solved

Companies receive thousands of support queries daily spanning multiple domains (billing, technical support, products, complaints). A single chatbot cannot handle all domains effectively.

**Solution:** A Multi-Agent system where each AI agent specializes in a single domain, coordinated by a central orchestrator that routes queries intelligently.

---

## 3. System Architecture

```
Customer
   |
   v
Web Chat Interface
   |
   v
Backend API Server
   |
   |---> Intent Detection ---> Agent Router
   |                                |
   |           .--------------------+---------------------.
   |           v                    v                     v                    v
   |        Billing             Technical              Product             Complaint
   |         Agent                Agent                Agent                Agent
   |           |                    |                     |                    |
   |           '--------------------+---------------------+--------------------'
   |                                |
   |                                v
   |                      Retrieval System (RAG)
   |                                |
   |                                v
   |                        Vector Database
   |                                |
   |                                v
   |                       Company Documents
   |
   |---> Conversation Memory
   |
   v
Response Aggregator -> Final Response
```

---

## 4. Technology Stack

### Frontend
| Technology | Purpose |
|---|---|
| React.js / Next.js | UI Framework |
| Tailwind CSS | Styling |
| Axios | HTTP Client |

### Backend
| Technology | Purpose |
|---|---|
| Python FastAPI *(recommended)* | REST API Server |
| Node.js + Express *(alternative)* | REST API Server |

### AI / ML
| Technology | Purpose |
|---|---|
| Google Gemini *(recommended)* | LLM |
| OpenAI GPT *(alternative)* | LLM |
| Llama 3 via Ollama/Groq *(alternative)* | LLM |
| sentence-transformers/all-MiniLM-L6-v2 | Embedding Model |
| BAAI/bge-small-en-v1.5 | Embedding Model |

### Storage
| Technology | Purpose |
|---|---|
| FAISS *(recommended)* | Vector Database |
| ChromaDB *(alternative)* | Vector Database |
| PostgreSQL / Supabase *(recommended)* | Relational Database |
| MongoDB Atlas *(alternative)* | Document Database |

### Deployment
| Layer | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Railway / Render |
| Database | Supabase / MongoDB Atlas |

### Key Python Libraries
`FastAPI` · `LangChain` · `LangGraph` · `FAISS` · `ChromaDB` · `sentence-transformers` · `openai` · `PyPDF` · `pandas` · `uvicorn`

---

## 5. Functional Modules

### Module 1 - User Authentication
- Login / Register
- Session management

### Module 2 - Chat Interface
- Chat window with send message
- Real-time conversation history
- Typing indicator

### Module 3 - Intent Detection Agent
Classifies each query into one of:
- `billing` | `refund` | `product` | `technical_support` | `complaint` | `general_faq`

### Module 4 - Agent Router
Routes queries to **one or multiple** specialized agents based on detected intent.

**Example:**
> *"I paid yesterday but Premium is still locked."*
> Routes to **Billing Agent** + **Technical Agent**

### Module 5 - Specialized Agents

| Agent | Handles |
|---|---|
| **Billing Agent** | Payments, subscriptions, invoices, refunds |
| **Technical Support Agent** | Login issues, password reset, installation, errors, bugs |
| **Product Agent** | Features, pricing, comparisons, availability |
| **Complaint Agent** | Complaints, escalations, customer dissatisfaction |
| **FAQ Agent** | Company policies, general questions, contact info |

### Module 6 - Knowledge Base
Company documents stored as PDFs and ingested into the vector database:
- `FAQ.pdf`, `UserManual.pdf`, `RefundPolicy.pdf`
- `Warranty.pdf`, `ShippingPolicy.pdf`, `Pricing.pdf`
- `Products.pdf`, `InstallationGuide.pdf`

### Module 7 - RAG Pipeline
```
Documents -> Chunk Text -> Generate Embeddings -> Store in Vector DB
                                                        |
User Query -> Embed Query -> Semantic Retrieval ---------'
                                   |
                          Pass context to LLM -> Generate Answer
```

### Module 8 - Conversation Memory
Stores per session:
- User message
- AI response
- Timestamp
- Session ID

### Module 9 - Analytics Dashboard *(Optional)*
- Number of conversations
- Agent usage statistics
- Response time
- Satisfaction scores

---

## 6. Folder Structure

```
customer-support-ai/
|
+-- frontend/
|   +-- components/
|   +-- pages/
|   +-- hooks/
|   +-- services/
|   +-- styles/
|
+-- backend/
|   +-- api/
|   +-- agents/
|   |     +-- billing.py
|   |     +-- technical.py
|   |     +-- product.py
|   |     +-- complaint.py
|   |     +-- faq.py
|   |     +-- router.py
|   +-- rag/
|   +-- embeddings/
|   +-- vectorstore/
|   +-- database/
|   +-- models/
|   +-- main.py
|
+-- knowledge_base/
|   +-- faq.pdf
|   +-- refund_policy.pdf
|   +-- shipping_policy.pdf
|   +-- warranty.pdf
|   +-- user_manual.pdf
|
+-- datasets/
+-- README.md
+-- requirements.txt
```

---

## 7. Datasets

| Dataset | Use Case | Source |
|---|---|---|
| **CFPB Consumer Complaint Dataset** | Real customer complaints & categories | Consumer Financial Protection Bureau |
| **Banking77** | Intent classification (77 banking intents) | Hugging Face |
| **DailyDialog** | Multi-turn conversation modeling | github.com/liuzeming01/XDailyDialog |
| **SQuAD v2** | Question-answering & retrieval | github.com/rajpurkar/SQuAD-explorer |
| **MS MARCO** | Semantic retrieval & QA | github.com/microsoft/MSMARCO-Question-Answering |

---

## 8. Implementation Phases

| Phase | Tasks |
|---|---|
| **1 - Planning** | Requirements, architecture design, UI wireframes, Git setup |
| **2 - Frontend** | Login page, chat interface, conversation history, API integration |
| **3 - Backend** | REST APIs, authentication, database, session management |
| **4 - AI Agents** | Intent detection, specialized agents, agent router |
| **5 - RAG Pipeline** | Document prep, chunking, embeddings, vector store, retrieval |
| **6 - LLM Integration** | Model integration, prompt engineering per agent, context injection |
| **7 - Testing** | Agent routing, retrieval quality, response time, edge cases |
| **8 - Deployment** | Frontend -> Vercel, Backend -> Railway/Render, DB -> Atlas/Supabase |

---

## 9. Evaluation Criteria

| Component | Marks |
|---|---|
| Frontend Design | 10 |
| Backend APIs | 15 |
| Multi-Agent Architecture | 20 |
| RAG Implementation | 20 |
| LLM Integration | 15 |
| Database Design | 10 |
| Documentation & Deployment | 10 |
| **Total** | **100** |

---

## 10. Deliverables

1. Source code (frontend + backend)
2. Project report (PDF)
3. README with setup instructions
4. Demonstration video *(compulsory)*
5. Knowledge base documents (PDFs)
6. Sample datasets (if used)
7. Deployment links (if deployed)

---

## 11. Bonus Enhancements

- Voice-enabled customer support
- Multilingual conversations
- Sentiment analysis for routing frustrated customers
- Automatic ticket creation
- Human-agent handoff
- Email and WhatsApp integration
- AI-generated conversation summaries
- Admin dashboard to update the knowledge base
- Customer satisfaction feedback and analytics

---

## 12. Fictional Company Context

Students should create a fictional company (e.g., **TechMart Electronics**) and author the knowledge base documents for that company. These documents form the RAG knowledge base used by all agents.

---

## 13. Key Design Decisions & Recommendations

| Decision | Recommended Choice | Alternatives |
|---|---|---|
| LLM | Google Gemini | OpenAI GPT, Llama 3 |
| Backend Framework | Python FastAPI | Node.js + Express |
| Vector DB | FAISS | ChromaDB, Pinecone |
| Relational DB | PostgreSQL (Supabase) | MongoDB |
| Frontend Deployment | Vercel | — |
| Backend Deployment | Railway / Render | — |
| Agent Orchestration | LangChain + LangGraph | Custom orchestrator |
