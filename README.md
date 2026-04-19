🛰️ DevHive: Enterprise Knowledge Discovery \& RAG Platform



\### \*\*The Neural Engine for High-Performance Knowledge Retrieval and Synthesis\*\*



\*\*DevHive\*\* is an advanced \*\*Retrieval-Augmented Generation (RAG)\*\* platform designed to transform static data into a high-speed, interactive intelligence hub. Engineered for enterprise-scale knowledge management, it enables teams to centralize documentation across multiple formats and platforms, delivering precise, context-aware answers in seconds.



\---



\## 🏗️ Technical Architecture



DevHive uses a decoupled, high-concurrency architecture optimized for sub-second vector retrieval and AI inference:



\* \*\*Frontend\*\*: Next.js 15 (App Router) • TypeScript • Framer Motion (Premium UI/UX) • Recharts (Neural Analytics)

\* \*\*Backend\*\*: FastAPI (Python 3.13) • AnyIO (Asynchronous Concurrency) • Pydantic V2 (Validation)

\* \*\*Vector Database\*\*: Supabase (PostgreSQL) • `pgvector` • HNSW indexing for O(log n) similarity search

\* \*\*AI Stack\*\*:

&#x20; \* \*\*Embeddings\*\*: `BAAI/bge-small-en-v1.5` via HuggingFace Inference API

&#x20; \* \*\*Inference\*\*: Groq Llama 3.1 8B (450+ tokens/sec for rapid synthesis)



\---



\## 🧠 Enterprise Features



\### 1. Neural Analytics Dashboard

A mission-control center for administrators to monitor system performance:

\* \*\*Query Velocity\*\*: Real-time tracking of search patterns over a 30-day timeline

\* \*\*System Confidence\*\*: Continuous monitoring of AI synthesis quality scores

\* \*\*Active Intelligence\*\*: Tracking of top intent patterns and most-searched technical terms



\### 2. Recursive Cloud Adapters

Deep integration with version control and collaboration tools:

\* \*\*Recursive GitHub Sync\*\*: Full-tree indexing of repositories including nested directories

\* \*\*Bridge Management\*\*: Centralized hub for managing external API connectors (Notion, Jira, GitHub)



\### 3. Smart Ingestion Pipeline (V2.1)

A robust multi-stage pipeline for document processing:

\* \*\*Content Deduplication\*\*: Automatic similarity checks (0.95 threshold) to prevent redundant indexing

\* \*\*Global Format Support\*\*: Native parsing for `PDF`, `DOCX`, `PPTX`, `XLSX`, `CSV`, `RTF`, `TXT`, `MD`

\* \*\*Background Processing\*\*: Embedding generation offloaded to background threads for zero-latency UI



\### 4. Granular RBAC System

Secure, role-based access control protecting enterprise data:

\* \*\*Admin\*\*: Full system visibility, analytics access, and global document management

\* \*\*Manager\*\*: Integration management and document synchronization rights

\* \*\*Employee\*\*: Workspace access and private document management



\---



\## 🛠️ Installation \& Setup



\### 1. Prerequisites

\* Python 3.11+

\* Node.js 20+

\* Supabase Project (with pgvector enabled)



\### 2. Environment Configuration



Create a `.env` file inside the `backend/` folder:



```env

HUGGINGFACE\_API\_KEY=hf\_...

SUPABASE\_URL=your\_project\_url

SUPABASE\_SERVICE\_ROLE\_KEY=your\_service\_role\_key

NEXT\_PUBLIC\_SUPABASE\_ANON\_KEY=your\_anon\_key

GROQ\_API\_KEY=gsk\_...

GROQ\_MODEL=llama-3.1-8b-instant

```



Create a `.env.local` file inside the `frontend/` folder:



```env

NEXT\_PUBLIC\_BACKEND\_URL=http://localhost:8000

NEXT\_PUBLIC\_SUPABASE\_URL=your\_project\_url

NEXT\_PUBLIC\_SUPABASE\_ANON\_KEY=your\_anon\_key

```



\### 3. Backend Setup



```bash

cd backend

pip install -r requirements.txt

uvicorn main:app --reload --port 8000

```



\### 4. Frontend Setup



```bash

cd frontend

npm install

npm run dev

```



\---



\## 🚀 Deployment



\* \*\*Backend\*\*: Deploy on Render as a FastAPI web service

\* \*\*Frontend\*\*: Deploy on Vercel — connect your GitHub repo and set environment variables



\---



© 2026 DevHive Enterprise | \*\*Designed for High-Speed Knowledge Discovery\*\*

