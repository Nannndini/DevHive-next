from typing import List

class ChunkingService:
    """Service for splitting text into smaller chunks with overlap"""
    
    @staticmethod
    def chunk_text(
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[str]:
        if not text or not text.strip():
            return []
            
        chunks: List[str] = []
        text_length = len(text)
        start = 0
        
        while start < text_length:
            # Determine initial end point
            end = min(start + chunk_size, text_length)
            
            # Try to find a natural break (space character) if we're not at the very end
            if end < text_length:
                boundary = text.rfind(" ", start, end)
                if boundary != -1 and boundary > start:
                    end = boundary
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            next_start = end - chunk_overlap
            
            # Avoid infinite loops / going backwards
            if next_start <= start:
                start = end
            else:
                start = next_start
                
            if start <= 0 and text_length > 0 and len(chunks) > 0:
                start = end
        
        return [c for c in chunks if c.strip()]

# Singleton instance
chunking_service = ChunkingService()
