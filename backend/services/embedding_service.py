import os
import asyncio
from typing import List

try:
    from huggingface_hub import AsyncInferenceClient
except ImportError:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class EmbeddingService:
    """Service for generating vector embeddings using official HuggingFace Inference Client"""
    
    def __init__(self):
        self._client = None
        hf_key = os.environ.get("HUGGINGFACE_API_KEY")
        model_name = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        
        if hf_key:
            self._client = AsyncInferenceClient(
                model=model_name,
                token=hf_key
            )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a piece of text using HF API with retries"""
        if not self._client:
            raise ValueError("Hugging Face client is not initialized. Please set HUGGINGFACE_API_KEY.")
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                embeddings = await self._client.feature_extraction(text)
                return embeddings if isinstance(embeddings, list) else embeddings.tolist()
            except Exception as e:
                error_str = str(e).lower()
                if ("503" in error_str or "429" in error_str) and attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                print(f"ERROR: HuggingFace feature_extraction failed on attempt {attempt+1}: {e}")
                raise e

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks with robust retries"""
        if not self._client:
            raise ValueError("Hugging Face client is not initialized")
            
        embeddings = []
        chunk_size = int(os.environ.get("EMBEDDING_BATCH_SIZE", "10"))
        
        for i in range(0, len(texts), chunk_size):
            batch = texts[i:i + chunk_size]
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    result = await self._client.feature_extraction(batch)
                    batch_embeddings = result if isinstance(result, list) else result.tolist()
                    embeddings.extend(batch_embeddings)
                    break
                except Exception as e:
                    error_str = str(e).lower()
                    if ("503" in error_str or "429" in error_str) and attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise e
                    
            if i + chunk_size < len(texts):
                await asyncio.sleep(0.5)

        return embeddings

# Singleton instance
embedding_service = EmbeddingService()
