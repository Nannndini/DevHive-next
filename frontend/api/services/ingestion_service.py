import logging
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models import Document
from api.services.chunking import chunking_service
from api.services.embedding_service import embedding_service, EmbeddingError

logger = logging.getLogger(__name__)

# cosine distance < 0.05  <=>  similarity > 0.95
DEDUP_DISTANCE = 0.05


class IngestionService:
    """Chunk -> embed -> semantic dedup (0.95) -> store in pgvector."""

    async def _check_duplicate_filename(self, db: Session, filename: str) -> bool:
        return db.query(Document).filter(Document.filename == filename).first() is not None

    def create_document(self, db: Session, filename: str, content: str) -> Document:
        file_type = "pdf" if filename.lower().endswith(".pdf") else "txt"
        doc = Document(
            title=filename, filename=filename, file_type=file_type,
            content=content, status="processing",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    async def process_document_async(self, doc_id: Any, filename: str, content: str) -> Dict[str, Any]:
        """Index an existing Document row. Always leaves status as 'complete' or 'failed'."""
        db = SessionLocal()
        try:
            chunks = chunking_service.chunk_text(content)
            if not chunks:
                self._set_status(db, doc_id, "failed")
                return {"status": "error", "reason": "no_content_extracted", "filename": filename}

            embeddings = await embedding_service.batch_generate_embeddings(chunks)

            saved = 0
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                emb_str = str(emb)
                dup = db.execute(
                    text("SELECT id FROM document_chunks "
                         "WHERE embedding <=> CAST(:e AS vector) < :d LIMIT 1"),
                    {"e": emb_str, "d": DEDUP_DISTANCE},
                ).fetchone()
                if dup:
                    continue
                db.execute(
                    text("INSERT INTO document_chunks (document_id, chunk_index, content, embedding) "
                         "VALUES (:doc, :idx, :content, CAST(:e AS vector))"),
                    {"doc": doc_id, "idx": i, "content": chunk, "e": emb_str},
                )
                saved += 1
            db.commit()

            self._set_status(db, doc_id, "complete")
            return {
                "status": "success", "document_id": str(doc_id),
                "chunks_processed": len(chunks), "chunks_saved": saved,
                "duplicates_skipped": len(chunks) - saved,
            }
        except EmbeddingError as e:
            logger.error("Embedding failed for %s: %s", filename, e)
            db.rollback()
            self._set_status(db, doc_id, "failed")
            return {"status": "error", "error_type": "embedding", "reason": str(e), "filename": filename}
        except Exception as e:
            logger.exception("Ingestion failed for %s", filename)
            db.rollback()
            self._set_status(db, doc_id, "failed")
            return {"status": "error", "reason": str(e), "filename": filename}
        finally:
            db.close()

    @staticmethod
    def _set_status(db: Session, doc_id: Any, status: str) -> None:
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.status = status
                db.commit()
        except Exception:
            db.rollback()
            logger.exception("Could not set status=%s for %s", status, doc_id)

    async def process_document(self, filename: str, content: str) -> Dict[str, Any]:
        """Create the row and index it (used by the Notion/GitHub sync)."""
        db = SessionLocal()
        try:
            if await self._check_duplicate_filename(db, filename):
                return {"status": "skipped", "reason": "exact_duplicate", "filename": filename}
            doc = self.create_document(db, filename, content)
            doc_id = doc.id
        finally:
            db.close()
        return await self.process_document_async(doc_id, filename, content)


ingestion_service = IngestionService()
