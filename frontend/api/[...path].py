from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api.database import engine, SessionLocal
from api.models import Base
from api.services.ingestion_service import ingestion_service
from api.routers import analytics, documents, search, auth_router
import io
import PyPDF2
from typing import Optional
import requests

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(auth_router.router, prefix="/api")

# create tables automatically
Base.metadata.create_all(bind=engine)
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER,
            content TEXT,
            embedding vector(384)
        )
    """))

@app.get("/api")
def root():
    return {"message": "DevHive backend running"}

@app.get("/api/overview")
async def root_overview():
    from api.routers.analytics import get_system_overview
    return await get_system_overview()

# Phase 3: Background Tasks implementation
@app.post("/api/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    is_private: Optional[bool] = Form(False)
):
    """
    Endpoint for uploading documents. Synchronous processing.
    """
    content = await file.read()
    
    if file.filename.lower().endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing PDF: {str(e)}")
    else:
        text_content = content.decode('utf-8', errors='ignore')
    
    # Process synchronously
    result = await ingestion_service.process_document(
        filename=file.filename, 
        content=text_content
    )
    
    return {
        "message": "Document processed successfully.",
        "filename": file.filename,
        "result": result
    }

# 4. Integrations
@app.post("/api/integrations")
async def create_integration(data: dict):
    return {"message": "Integration created successfully", "id": data.get("id", "int_" + str(hash(data.get("platform_name"))))}

@app.post("/api/integrations/{id}/sync")
async def sync_integration(id: str, data: dict):
    platform = data.get("platform_type", "").lower()
    token = data.get("api_token", "")
    
    if not token:
        raise HTTPException(status_code=400, detail="API Token is required for synchronization")
        
    pages_indexed = 0
    
    try:
        if platform == "notion":
            headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            response = requests.post("https://api.notion.com/v1/search", headers=headers, json={"filter": {"value": "page", "property": "object"}})
            
            if not response.ok:
                raise HTTPException(status_code=response.status_code, detail=f"Notion API error: {response.text}")
                
            results = response.json().get("results", [])
            for page in results:
                page_id = page["id"]
                title_prop = page.get("properties", {}).get("title", {}).get("title", [])
                title = title_prop[0]["plain_text"] if title_prop else f"Notion Page {page_id}"
                
                text_content = f"Notion Page: {title}\nID: {page_id}\nURL: {page.get('url', '')}"
                
                await ingestion_service.process_document(
                    filename=f"notion_{page_id}.txt",
                    content=text_content
                )
                pages_indexed += 1
                
        elif platform == "github":
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get("https://api.github.com/user/repos", headers=headers)
            
            if not response.ok:
                raise HTTPException(status_code=response.status_code, detail=f"GitHub API error: {response.text}")
                
            repos = response.json()
            for repo in repos:
                text_content = f"GitHub Repository: {repo.get('name')}\nDescription: {repo.get('description', '')}\nURL: {repo.get('html_url')}"
                await ingestion_service.process_document(
                    filename=f"github_{repo.get('name')}.txt",
                    content=text_content
                )
                pages_indexed += 1
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"message": f"Integration {id} synced successfully", "pages_indexed": pages_indexed}
