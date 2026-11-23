import os
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from groq import Groq
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.database import SessionLocal
from api.services.embedding_service import embedding_service, EmbeddingError

logger = logging.getLogger(__name__)

# llama-3.1-8b-instant was shut down on Groq's free/dev tier on 2026-08-16.
# Override with GROQ_MODEL if Groq changes the lineup again.
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"

router = APIRouter(prefix="/search", tags=["search"])


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


def _groq_client():
    key = os.environ.get("GROQ_API_KEY")
    return Groq(api_key=key) if key else None


@router.post("")
async def search_documents(
    request: SearchQuery,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """pgvector cosine search + optional Groq synthesis."""
    try:
        query_embedding = await embedding_service.generate_embedding(request.query)
    except EmbeddingError as e:
        logger.error("Query embedding failed: %s", e)
        raise HTTPException(status_code=502, detail=f"Embedding service error: {e}")

    try:
        rows = db.execute(
            text("""
                SELECT c.id AS chunk_id, c.content, c.chunk_index, d.title, d.id AS doc_id,
                       1 - (c.embedding <=> CAST(:e AS vector)) AS similarity
                FROM document_chunks c
                JOIN documents d ON c.document_id = d.id
                ORDER BY c.embedding <=> CAST(:e AS vector) ASC
                LIMIT :k
            """),
            {"e": str(query_embedding), "k": request.top_k},
        ).fetchall()
    except Exception as e:
        logger.exception("Vector search failed")
        raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")

    chunks = [
        {
            "id": str(r.chunk_id),
            "text": r.content,
            "document_id": str(r.title),  # the UI displays the title here
            "similarity": float(r.similarity),
        }
        for r in rows
        if r.similarity is not None and float(r.similarity) >= request.min_similarity
    ]
    sources = sorted({c["document_id"] for c in chunks})

    ai_answer = None
    if chunks and request.use_ai:
        client = _groq_client()
        if client is None:
            ai_answer = "AI synthesis unavailable: GROQ_API_KEY is not set."
        else:
            context = "\n\n".join(f"[{c['document_id']}]: {c['text']}" for c in chunks)
            prompt = (
                "You are an enterprise AI assistant. Answer strictly from the context. "
                "If the answer is not in the context, say 'I cannot answer this based on "
                "the available documents.'\n\n"
                f"Context:\n{context}\n\nQuery: {request.query}"
            )
            try:
                resp = client.chat.completions.create(
                    model=os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL),
                    messages=[{"role": "user", "content": prompt}],
                )
                ai_answer = resp.choices[0].message.content
            except Exception as e:
                logger.exception("Groq generation failed")
                ai_answer = f"AI synthesis failed ({type(e).__name__}). Retrieved chunks are shown below."

    return {"query": request.query, "ai_answer": ai_answer, "sources": sources, "chunks": chunks}
