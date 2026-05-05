import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from services.chunking import chunking_service
from services.embedding_service import embedding_service
from models import Document
from database import SessionLocal

class IngestionService:
    """Core pipeline for processing and ingesting documents with deduplication"""
    
    def __init__(self):
        self.similarity_threshold = 0.95
        
    async def _check_duplicate_filename(self, db: Session, filename: str) -> bool:
        """Check if a file with this exact name already exists in the DB"""
        # Based on current models.Document containing 'title'
        existing = db.query(Document).filter(Document.title == filename).first()
        return existing is not None
        
    async def process_document(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Main pipeline: Check duplicates -> Chunk -> Embed -> Save
        Designed to be run as a FastAPI BackgroundTask.
        """
        db = SessionLocal()
        try:
            # 1. Exact Filename Deduplication Check
            if await self._check_duplicate_filename(db, filename):
                return {"status": "skipped", "reason": "exact_duplicate", "filename": filename}
                
            # 2. Chunking
            chunks = chunking_service.chunk_text(content)
            if not chunks:
                return {"status": "error", "reason": "no_content_extracted", "filename": filename}
                
            # 3. Generate Embeddings for chunks
            embeddings = await embedding_service.batch_generate_embeddings(chunks)
            
            # 4. Save parent Document to Database
            new_doc = Document(title=filename, content=content)
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            
            # Ensure chunks table exists for pgvector
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER,
                    content TEXT,
                    embedding vector(384) -- BAAI/bge-small-en-v1.5 outputs 384d
                )
            """))
            db.commit()
            
            # 5. Semantic Deduplication & Saving Chunks
            chunks_saved = 0
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                # Convert embedding list to pgvector formatted string "[0.1, 0.2, ...]"
                embedding_str = str(embedding)
                
                # Check 0.95 cosine similarity deduplication
                # cosine distance (<=>) ranges from 0 (perfect match) to 2 (perfect opposite)
                # similarity = 1 - distance. So similarity > 0.95 is distance < 0.05
                duplicate_check_query = text("""
                    SELECT id FROM document_chunks 
                    WHERE embedding <=> :embedding::vector < 0.05
                    LIMIT 1
                """)
                
                duplicate = db.execute(duplicate_check_query, {"embedding": embedding_str}).fetchone()
                
                if not duplicate:
                    # Save unique chunk
                    insert_query = text("""
                        INSERT INTO document_chunks (document_id, chunk_index, content, embedding)
                        VALUES (:doc_id, :idx, :content, :embedding::vector)
                    """)
                    db.execute(insert_query, {
                        "doc_id": new_doc.id,
                        "idx": i,
                        "content": chunk_text,
                        "embedding": embedding_str
                    })
                    chunks_saved += 1
                    
            db.commit()
            
            return {
                "status": "success", 
                "document_id": new_doc.id, 
                "chunks_processed": len(chunks),
                "chunks_saved": chunks_saved,
                "duplicates_skipped": len(chunks) - chunks_saved
            }
            
        except Exception as e:
            print(f"Error processing document {filename}: {e}")
            db.rollback()
            return {"status": "error", "reason": str(e), "filename": filename}
        finally:
            db.close()

ingestion_service = IngestionService()
