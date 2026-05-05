from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base
from services.ingestion_service import ingestion_service
from routers import analytics, documents, search, auth_router

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

app.include_router(analytics.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(auth_router.router)

# create tables automatically
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "DevHive backend running"}


# Phase 3: Background Tasks implementation
@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...)
):
    """
    Endpoint for uploading documents. Synchronous processing.
    """
    content = await file.read()
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