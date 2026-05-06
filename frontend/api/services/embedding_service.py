import os
import asyncio
from typing import List
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class EmbeddingService:
    """Service for generating vector embeddings using official HuggingFace Inference Client via HTTP requests"""
    
    def __init__(self):
        self.hf_key = os.environ.get("HUGGINGFACE_API_KEY")
        self.model_name = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}"
        
        self.headers = {"Authorization": f"Bearer {self.hf_key}"} if self.hf_key else {}

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a piece of text using HF API with retries"""
        if not self.hf_key:
            # Fallback to zeros for testing if API key is not configured, avoiding crashing
            return [0.0] * 384
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json={"inputs": text})
                if response.status_code == 200:
                    result = response.json()
                    # Some models return nested lists, flatten if necessary
                    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                        return result[0]
                    return result
                elif response.status_code in [503, 429] and attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    print(f"HF API Error: {response.text}")
                    if attempt == max_retries - 1:
                        # Fallback for demo
                        return [0.0] * 384
            except Exception as e:
                print(f"ERROR: HuggingFace feature_extraction failed on attempt {attempt+1}: {e}")
                if attempt == max_retries - 1:
                    # Fallback for demo
                    return [0.0] * 384
                await asyncio.sleep(2 ** attempt)

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks with robust retries"""
        if not self.hf_key:
            return [[0.0] * 384 for _ in texts]
            
        embeddings = []
        chunk_size = int(os.environ.get("EMBEDDING_BATCH_SIZE", "10"))
        
        for i in range(0, len(texts), chunk_size):
            batch = texts[i:i + chunk_size]
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(self.api_url, headers=self.headers, json={"inputs": batch})
                    if response.status_code == 200:
                        batch_result = response.json()
                        embeddings.extend(batch_result)
                        break
                    elif response.status_code in [503, 429] and attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        print(f"HF API Error batch: {response.text}")
                        if attempt == max_retries - 1:
                            embeddings.extend([[0.0] * 384 for _ in batch])
                except Exception as e:
                    if attempt == max_retries - 1:
                        embeddings.extend([[0.0] * 384 for _ in batch])
                    await asyncio.sleep(2 ** attempt)
                    
            if i + chunk_size < len(texts):
                await asyncio.sleep(0.5)

        return embeddings

# Singleton instance
embedding_service = EmbeddingService()
