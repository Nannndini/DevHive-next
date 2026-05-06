from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Dict, Any

from database import SessionLocal
from services.embedding_service import embedding_service

import os
from groq import Groq

# Initialize Groq client
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
except Exception:
    client = None

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
    top_k: int = 5
    min_similarity: float = 0.3
    use_ai: bool = True

@router.post("/")
async def search_documents(request: SearchQuery, db: Session = Depends(get_db)):
    """
    Search documents using pgvector cosine similarity and return Groq AI synthesis.
    """
    try:
        # 1. Generate embedding for the search query
        query_embedding = await embedding_service.generate_embedding(request.query)
        embedding_str = str(query_embedding)
        
        # 2. Perform pgvector similarity search
        search_query = text("""
            SELECT c.id as chunk_id, c.content, c.chunk_index, d.title, d.id as doc_id, 1 - (c.embedding <=> :embedding::vector) as similarity
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.embedding <=> :embedding::vector ASC
            LIMIT :top_k
        """)
        
        results = db.execute(search_query, {"embedding": embedding_str, "top_k": request.top_k}).fetchall()
        
        formatted_results = []
        for row in results:
            if float(row.similarity) >= request.min_similarity:
                formatted_results.append({
                    "id": str(row.chunk_id),
                    "text": row.content,
                    "document_id": str(row.title), # Use title as document_id for frontend display
                    "similarity": float(row.similarity)
                })
            
        ai_answer = None
        sources = list(set([r["document_id"] for r in formatted_results]))
        
        # 3. Generate AI synthesis using Groq
        if formatted_results and request.use_ai and client:
            context_blocks = [f"[{r['document_id']}]: {r['text']}" for r in formatted_results]
            context_text = "\n\n".join(context_blocks)
            
            prompt = f"You are an enterprise AI assistant. Answer the following query strictly based on the provided context. If the answer is not in the context, say 'I cannot answer this based on the available documents.'\n\nContext:\n{context_text}\n\nQuery: {request.query}"
            
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=os.environ.get("GROQ_MODEL", "llama-3-8b-instruct") # actually it's llama-3.1-8b-instant usually but this falls back if not set
                )
                ai_answer = response.choices[0].message.content
            except Exception as e:
                print(f"Groq generation error: {e}")
                ai_answer = "Error generating AI synthesis. Please try again."

        return {
            "query": request.query, 
            "ai_answer": ai_answer,
            "sources": sources,
            "chunks": formatted_results
        }
        
    except Exception as e:
        print(f"Search error: {e}")
        return {"query": request.query, "ai_answer": f"Error: {str(e)}", "sources": [], "chunks": []}
