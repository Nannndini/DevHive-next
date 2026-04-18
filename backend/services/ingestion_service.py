import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.services.chunking import chunking_service
from backend.services.embedding_service import embedding_service
from backend.models import Document

class IngestionService:
    """Core pipeline for processing and ingesting documents with deduplication"""
    
    def __init__(self):
        self.similarity_threshold = 0.95
        
    async def _check_duplicate_filename(self, db: Session, filename: str) -> bool:
        """Check if a file with this exact name already exists in the DB"""
        # Based on current models.Document containing 'title'
        existing = db.query(Document).filter(Document.title == filename).first()
        return existing is not None
        
    async def process_document(self, db: Session, filename: str, content: str) -> Dict[str, Any]:
        """
        Main pipeline: Check duplicates -> Chunk -> Embed -> Save
        Designed to be run as a FastAPI BackgroundTask.
        """
        try:
            # 1. Exact Filename Deduplication Check
            if await self._check_duplicate_filename(db, filename):
                return {"status": "skipped", "reason": "exact_duplicate", "filename": filename}
                
            # 2. Chunking
            chunks = chunking_service.chunk_text(content)
            if not chunks:
                return {"status": "error", "reason": "no_content_extracted", "filename": filename}
                
            # 3. Generate Embeddings for chunks
            # In a real scenario, you'd store these vectors if using pgvector
            embeddings = await embedding_service.batch_generate_embeddings(chunks)
            
            # Semantic Deduplication placeholder
            # If the vectors match > 0.95 with existing DB entries, skip
            # Currently requires pgvector or similar similarity search implementation which would go here
            
            # 4. Save to Database
            # We save the parent document. To fully support RAG, you'd also save Chunks + Vectors.
            new_doc = Document(title=filename, content=content)
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            
            return {
                "status": "success", 
                "document_id": new_doc.id, 
                "chunks_processed": len(chunks)
            }
            
        except Exception as e:
            print(f"Error processing document {filename}: {e}")
            db.rollback()
            return {"status": "error", "reason": str(e), "filename": filename}

ingestion_service = IngestionService()
