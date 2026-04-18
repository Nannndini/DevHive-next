from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base
from services.ingestion_service import ingestion_service
from routers import analytics

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

# create tables automatically
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "DevHive backend running"}
def require_manager(user=Depends(get_current_user)):
    if user.get("role") not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    return user

@app.get("/manager/team-docs")
async def manager_team_docs(user=Depends(require_manager)):
    # Assuming supabase is defined elsewhere or client is injected. Placeholder based on original code.
    try:
        docs = supabase.table("documents").select("id, title, source, file_type, created_at, user_id").order("created_at", desc=True).execute()
        return {"documents": docs.data}
    except Exception as e:
        return {"error": str(e), "message": "Supabase client not initialized or missing"}

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