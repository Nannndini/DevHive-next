from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base
from services.ingestion_service import ingestion_service
from routers import analytics, documents, search

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

# create tables automatically
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "DevHive backend running"}


# Phase 3: Background Tasks implementation
@app.post("/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint for uploading documents. Runs processing via background tasks 
    to prevent blocking and Vercel timeouts.
    """
    content = await file.read()
    text_content = content.decode('utf-8', errors='ignore')
    
    # Add to background tasks
    background_tasks.add_task(
        ingestion_service.process_document, 
        db=db, 
        filename=file.filename, 
        content=text_content
    )
    
    return {
        "message": "Document uploaded successfully. Processing started in background.",
        "filename": file.filename
    }