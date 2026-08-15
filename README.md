# 🤖 Multi-Agent AI Customer Support Assistant

A production-ready, multi-agent customer support assistant powered by **Google Gemini**, **FastAPI**, **Next.js**, and **FAISS** vector search.

## 📁 Repository Structure

- [`customer-support-ai/`](customer-support-ai/): Main application source code
  - [`frontend/`](customer-support-ai/frontend/): Next.js 14 Web Application (TypeScript, Tailwind CSS, Lucide icons)
  - [`backend/`](customer-support-ai/backend/): FastAPI backend (Agents, RAG pipeline, Database models, Vector store)
  - [`knowledge_base/`](customer-support-ai/knowledge_base/): TechMart Electronics policy and product PDF documents
  - [`datasets/`](customer-support-ai/datasets/): Evaluation and testing datasets
- [`Docs/`](Docs/): Architectural design and implementation specifications
  - [`Docs/architecture.md`](Docs/architecture.md): Complete architecture document
  - [`Docs/implementation_plan.md`](Docs/implementation_plan.md): 8-Phase implementation roadmap

## 🚀 Quick Start & Deployment

- **Local Setup & Development:** See [`customer-support-ai/README.md`](customer-support-ai/README.md)
- **Production Deployment (Render & Vercel):** See [`customer-support-ai/DEPLOYMENT.md`](customer-support-ai/DEPLOYMENT.md)
- **Docker Compose:** Run `docker-compose up --build` inside `customer-support-ai/`

