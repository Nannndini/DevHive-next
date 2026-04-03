# 🧠 DevHive — Knowledge Transfer Platform v2.0

AI-powered knowledge management platform. Upload documents, search semantically, and get LLaMA-powered answers.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | Supabase (PostgreSQL + pgvector) |
| AI Embeddings | SentenceTransformer (all-MiniLM-L6-v2) |
| AI Q&A | Groq LLaMA 3 (8B) |
| Auth | Supabase Auth + JWT |
| Deployment | Vercel (frontend) + Render (backend) |

---

## ⚡ Quick Setup

### Step 1 — Supabase Schema
1. Go to [Supabase Dashboard](https://supabase.com/dashboard) → SQL Editor
2. Paste the contents of `backend/schema.sql`
3. Click **Run**

### Step 2 — Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Fill in your keys in .env
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Step 3 — Frontend

```bash
cd frontend
npm install
# Edit .env.local — set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Frontend runs at: http://localhost:3000

---

## 🚀 Deployment

### Backend → Render
1. Push `backend/` folder to GitHub
2. Create new Web Service on Render
3. Set environment variables (from `backend/.env`)
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel
1. Push `frontend/` folder to GitHub
2. Import to Vercel
3. Set `NEXT_PUBLIC_API_URL` = your Render backend URL

---

## 📁 Project Structure

```
devhive/
├── backend/
│   ├── main.py          # FastAPI app + all routes
│   ├── rag.py           # RAG pipeline (embed + search + answer)
│   ├── auth.py          # JWT utilities
│   ├── database.py      # Supabase client
│   ├── file_utils.py    # PDF/DOCX/TXT extraction
│   ├── config.py        # Settings
│   ├── schema.sql       # Run this in Supabase first!
│   └── requirements.txt
└── frontend/
    ├── pages/
    │   ├── index.js     # Redirect
    │   ├── login.js     # Auth
    │   ├── register.js  # Auth
    │   ├── dashboard.js # Home
    │   ├── documents.js # Upload + manage
    │   ├── search.js    # Semantic search
    │   ├── ask.js       # AI Q&A chat
    │   ├── stats.js     # Analytics
    │   └── admin.js     # Admin panel
    ├── components/
    │   ├── Layout.js    # Sidebar layout
    │   └── withAuth.js  # Auth HOC
    └── lib/
        ├── api.js       # Axios client
        └── auth.js      # Auth context
```

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | /auth/register | Register |
| POST | /auth/login | Login |
| GET | /auth/me | Current user |
| POST | /documents/ingest/text | Add text |
| POST | /documents/ingest/file | Upload file |
| GET | /documents | List documents |
| DELETE | /documents/{id} | Delete document |
| POST | /search | Semantic search |
| POST | /ask | AI Q&A |
| GET | /stats | Analytics |
| GET | /audit-logs | Audit logs (admin) |
| GET | /admin/users | All users (admin) |
| PATCH | /admin/users/{id}/role | Change role (admin) |

## Team

- 23B81A0532 - P.Nandini Naidu
- 23B81A0545 - K.Sarayu Reddy  
- 23B81A0550 - M.Sri Vardhan

CVR College of Engineering — Industry Oriented Mini Project 2026
