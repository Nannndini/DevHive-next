"""Single FastAPI app for both Vercel entrypoints (index.py, [...path].py) and local dev.

Files starting with an underscore in api/ are not deployed as separate functions.
"""
import io
import logging
from typing import Optional

import PyPDF2
from fastapi import (
    Depends, FastAPI, File, HTTPException, Query, UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

from api.auth import get_current_user
from api.models import Document
from api.database import SessionLocal, ensure_schema
from api.routers import analytics, auth_router, documents, integrations, search
from api.services.ingestion_service import ingestion_service

logger = logging.getLogger(__name__)


def _init_schema():
    try:
        ensure_schema()
    except Exception:
        logger.exception("ensure_schema failed (continuing; requests will surface DB errors)")


app = FastAPI(dependencies=[Depends(_init_schema)])

# Same-origin in production (Next.js serves the UI and /api). Restrict instead of "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (analytics, documents, search, auth_router, integrations):
    app.include_router(r.router, prefix="/api")


@app.get("/api")
def root():
    return {"message": "DevHive backend running"}


def _extract_text(filename: str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing PDF: {e}")
    return content.decode("utf-8", errors="ignore")


@app.post("/api/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    is_private: Optional[bool] = Query(False),
    user: dict = Depends(get_current_user),
):
    """Upload -> chunk -> embed -> store, all inside the request.

    Vercel can freeze/kill a serverless function once the response is sent, so
    BackgroundTasks left documents stuck in 'processing'. Doing the work before
    responding means the status is always final ('complete' / 'failed').
    """
    text_content = _extract_text(file.filename, await file.read())

    def _create():
        db = SessionLocal()
        try:
            exists = db.query(Document).filter_by(filename=file.filename).first()
            if exists:
                return None
            return ingestion_service.create_document(db, file.filename, text_content).id
        finally:
            db.close()

    doc_id = await run_in_threadpool(_create)
    if doc_id is None:
        return {
            "status": "duplicate",
            "message": f"Document '{file.filename}' already exists.",
            "filename": file.filename,
        }

    result = await ingestion_service.process_document_async(doc_id, file.filename, text_content)
    if result.get("status") != "success":
        raise HTTPException(status_code=502 if result.get("error_type") == "embedding" else 500,
                            detail=f"Ingestion failed: {result.get('reason')}")
    return {
        "status": "complete",
        "document_id": str(doc_id),
        "filename": file.filename,
        "chunks_saved": result["chunks_saved"],
        "duplicates_skipped": result["duplicates_skipped"],
    }

