from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from api.database import SessionLocal
from api.models import Document
from api.auth import get_current_user, RoleChecker

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
def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: Dict[str, Any] = Depends(get_current_user)):
    """List all documents."""
    try:
        docs = db.query(Document).offset(skip).limit(limit).all()
        # Format to match what the frontend expects, including status and created_at
        return {"documents": [
            {
                "id": str(d.id), 
                "title": d.title, 
                "filename": d.filename,
                "source": "uploaded", 
                "status": d.status,
                "created_at": d.created_at.isoformat() if d.created_at else None
            } for d in docs
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database retrieval failed: {str(e)}")

@router.get("/{doc_id}")
def get_document(doc_id: str, db: Session = Depends(get_db), user: Dict[str, Any] = Depends(get_current_user)):
    """Get a specific document by ID."""
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "id": str(doc.id), 
            "title": doc.title, 
            "filename": doc.filename,
            "content": doc.content, 
            "status": doc.status,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db), user: Dict[str, Any] = Depends(RoleChecker(["admin", "manager"]))):
    """Delete a document by ID."""
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        db.delete(doc)
        db.commit()
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database deletion failed: {str(e)}")
