from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base
from routers import analytics, documents, search, auth_router, integrations
from models import Document
from services.ingestion_service import ingestion_service
import io
import PyPDF2
from typing import Optional
from auth import get_current_user

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
app.include_router(integrations.router, prefix="/api")

# create tables automatically
Base.metadata.create_all(bind=engine)

@app.get("/api")
def root():
    return {"message": "DevHive backend running"}

@app.get("/api/overview")
async def root_overview():
    from routers.analytics import get_system_overview
    return await get_system_overview()

# Phase 3: Background Tasks implementation
@app.post("/api/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    is_private: Optional[bool] = Form(False),
    user: dict = Depends(get_current_user)
):
    """
    Endpoint for uploading documents. Asynchronous background processing.
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
    
    # Check exact duplicate filename synchronously
    db = SessionLocal()
    try:
        if await ingestion_service._check_duplicate_filename(db, file.filename):
            # Keep frontend compatible status return
            return {
                "status": "duplicate",
                "message": f"Document '{file.filename}' already exists.",
                "filename": file.filename
            }
            
        # Create parent Document in database with status "processing"
        file_type = "pdf" if file.filename.lower().endswith(".pdf") else "txt"
        new_doc = Document(
            title=file.filename,
            filename=file.filename,
            file_type=file_type,
            content=text_content,
            status="processing"
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        doc_id = new_doc.id
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during document initialization: {str(e)}")
    finally:
        db.close()
        
    # Kick off processing in the background
    background_tasks.add_task(
        ingestion_service.process_document_async,
        doc_id,
        file.filename,
        text_content
    )
    
    return {
        "status": "processing",
        "document_id": str(doc_id),
        "filename": file.filename,
        "message": "Document ingestion queued for background processing."
    } 
