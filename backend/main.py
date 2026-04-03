from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from jose import JWTError

from config import settings
from database import supabase
from auth import create_access_token, decode_token
from rag import store_document_with_embeddings, semantic_search, answer_question
from file_utils import extract_text_from_file

app = FastAPI(title="DevHive - Knowledge Transfer Platform", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth helpers ──────────────────────────────────────────────────────────────

def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class IngestTextRequest(BaseModel):
    title: str
    content: str
    source: str = "manual"

class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    threshold: float = 0.3

class QuestionRequest(BaseModel):
    question: str

# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.post("/auth/register")
async def register(body: RegisterRequest):
    try:
        res = supabase.auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {"data": {"full_name": body.full_name}}
        })
        if not res.user:
            raise HTTPException(status_code=400, detail="Registration failed")

        # Get profile role
        profile = supabase.table("profiles").select("role").eq("id", res.user.id).execute()
        role = profile.data[0]["role"] if profile.data else "user"

        token = create_access_token({
            "sub": res.user.id,
            "email": body.email,
            "role": role,
            "full_name": body.full_name
        })
        return {"token": token, "user": {"id": res.user.id, "email": body.email, "role": role, "full_name": body.full_name}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(body: LoginRequest):
    try:
        res = supabase.auth.sign_in_with_password({"email": body.email, "password": body.password})
        if not res.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        profile = supabase.table("profiles").select("role, full_name").eq("id", res.user.id).execute()
        role = profile.data[0]["role"] if profile.data else "user"
        full_name = profile.data[0]["full_name"] if profile.data else ""

        token = create_access_token({
            "sub": res.user.id,
            "email": body.email,
            "role": role,
            "full_name": full_name
        })
        return {"token": token, "user": {"id": res.user.id, "email": body.email, "role": role, "full_name": full_name}}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    return user

# ── Documents ─────────────────────────────────────────────────────────────────

@app.post("/documents/ingest/text")
async def ingest_text(body: IngestTextRequest, user=Depends(get_current_user)):
    result = store_document_with_embeddings(
        user_id=user["sub"],
        title=body.title,
        content=body.content,
        source=body.source
    )
    if result.get("duplicate"):
        return {"message": "Duplicate content detected", "duplicate": True, **result}
    return {"message": "Document ingested successfully", "duplicate": False, **result}

@app.post("/documents/ingest/file")
async def ingest_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    file_bytes = await file.read()
    try:
        content, file_type = extract_text_from_file(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not content.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")

    result = store_document_with_embeddings(
        user_id=user["sub"],
        title=file.filename,
        content=content,
        source="upload",
        file_type=file_type,
        metadata={"original_filename": file.filename, "size_bytes": len(file_bytes)}
    )

    # Audit log
    supabase.table("audit_logs").insert({
        "user_id": user["sub"],
        "action": "file_upload",
        "resource": file.filename,
        "details": {"file_type": file_type, "duplicate": result.get("duplicate", False)}
    }).execute()

    if result.get("duplicate"):
        return {"message": "Duplicate file detected", "duplicate": True, **result}
    return {"message": f"File '{file.filename}' ingested successfully", "duplicate": False, **result}

@app.get("/documents")
async def list_documents(user=Depends(get_current_user)):
    if user.get("role") == "admin":
        docs = supabase.table("documents").select("id, title, source, file_type, created_at, user_id").order("created_at", desc=True).execute()
    else:
        docs = supabase.table("documents").select("id, title, source, file_type, created_at").eq("user_id", user["sub"]).order("created_at", desc=True).execute()
    return {"documents": docs.data}

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, user=Depends(get_current_user)):
    doc = supabase.table("documents").select("user_id").eq("id", doc_id).execute()
    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.data[0]["user_id"] != user["sub"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    supabase.table("embeddings").delete().eq("document_id", doc_id).execute()
    supabase.table("documents").delete().eq("id", doc_id).execute()

    supabase.table("audit_logs").insert({
        "user_id": user["sub"],
        "action": "document_delete",
        "resource": doc_id
    }).execute()

    return {"message": "Document deleted"}

# ── Search & Q&A ──────────────────────────────────────────────────────────────

@app.post("/search")
async def search(body: SearchRequest, user=Depends(get_current_user)):
    results = semantic_search(body.query, limit=body.limit, threshold=body.threshold)

    supabase.table("search_logs").insert({
        "user_id": user["sub"],
        "query": body.query,
        "results_count": len(results)
    }).execute()

    return {"query": body.query, "results": results, "count": len(results)}

@app.post("/ask")
async def ask(body: QuestionRequest, user=Depends(get_current_user)):
    result = answer_question(body.question, user["sub"])
    return result

# ── Analytics ─────────────────────────────────────────────────────────────────

@app.get("/stats")
async def get_stats(user=Depends(get_current_user)):
    if user.get("role") == "admin":
        docs = supabase.table("documents").select("id, source, file_type").execute()
        users = supabase.table("profiles").select("id").execute()
        searches = supabase.table("search_logs").select("id").execute()
        qa = supabase.table("qa_logs").select("id").execute()
        embeddings = supabase.table("embeddings").select("id").execute()
    else:
        docs = supabase.table("documents").select("id, source, file_type").eq("user_id", user["sub"]).execute()
        users = None
        searches = supabase.table("search_logs").select("id").eq("user_id", user["sub"]).execute()
        qa = supabase.table("qa_logs").select("id").eq("user_id", user["sub"]).execute()
        embeddings = supabase.table("embeddings").select("id").execute()

    source_counts = {}
    type_counts = {}
    for d in (docs.data or []):
        source_counts[d["source"]] = source_counts.get(d["source"], 0) + 1
        type_counts[d.get("file_type", "txt")] = type_counts.get(d.get("file_type", "txt"), 0) + 1

    return {
        "total_documents": len(docs.data or []),
        "total_embeddings": len(embeddings.data or []),
        "total_searches": len(searches.data or []),
        "total_qa": len(qa.data or []),
        "total_users": len(users.data) if users else None,
        "source_breakdown": source_counts,
        "type_breakdown": type_counts
    }

@app.get("/audit-logs")
async def get_audit_logs(user=Depends(require_admin)):
    logs = supabase.table("audit_logs").select("*").order("created_at", desc=True).limit(100).execute()
    return {"logs": logs.data}

@app.get("/admin/users")
async def list_users(user=Depends(require_admin)):
    users = supabase.table("profiles").select("*").order("created_at", desc=True).execute()
    return {"users": users.data}

@app.patch("/admin/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, admin=Depends(require_admin)):
    if role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    supabase.table("profiles").update({"role": role}).eq("id", user_id).execute()
    return {"message": f"User role updated to {role}"}

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}

@app.get("/")
async def root():
    return {"message": "DevHive KTP API v2.0", "docs": "/docs"}
