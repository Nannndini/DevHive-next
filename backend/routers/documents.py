from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import SessionLocal
from models import Document

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all documents."""
    docs = db.query(Document).offset(skip).limit(limit).all()
    # Format to match what the frontend expects
    return {"documents": [{"id": d.id, "title": d.title, "source": "uploaded"} for d in docs]}

@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "title": doc.title, "content": doc.content}

@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document by ID."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
