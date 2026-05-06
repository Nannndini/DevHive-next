from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base
from services.ingestion_service import ingestion_service
from routers import analytics, documents, search, auth_router
import io
import PyPDF2

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
    file: UploadFile = File(...)
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
