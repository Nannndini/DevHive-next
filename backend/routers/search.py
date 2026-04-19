from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Dict, Any

from database import SessionLocal
from services.embedding_service import embedding_service

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SearchQuery(BaseModel):
    query: str

@router.post("/")
async def search_documents(request: SearchQuery, db: Session = Depends(get_db)):
    """
    Search documents using pgvector cosine similarity.
    Requires the document_chunks table with embeddings to exist.
    """
    try:
        # 1. Generate embedding for the search query
        query_embedding = await embedding_service.generate_embedding(request.query)
        embedding_str = str(query_embedding)
        
        # 2. Perform pgvector similarity search against document_chunks
        # Order by cosine distance (<=>) and limit to top 5 results
        search_query = text("""
            SELECT c.content, c.chunk_index, d.title, 1 - (c.embedding <=> :embedding::vector) as similarity
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.embedding <=> :embedding::vector ASC
            LIMIT 5
        """)
        
        results = db.execute(search_query, {"embedding": embedding_str}).fetchall()
        
        formatted_results = []
        for row in results:
            formatted_results.append({
                "content": row.content,
                "title": row.title,
                "chunk": row.chunk_index,
                "score": round(float(row.similarity), 4)
            })
            
        return {"query": request.query, "results": formatted_results}
        
    except Exception as e:
        print(f"Search error: {e}")
        # Fallback if table doesn't exist yet or pgvector isn't setup
        return {"query": request.query, "results": [], "error": str(e)}
