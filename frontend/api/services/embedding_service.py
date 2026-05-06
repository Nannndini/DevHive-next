import os
import asyncio
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class EmbeddingService:
    """Service for generating vector embeddings using Groq API"""
    
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.model_name = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text-v1_5")
        
        if self.api_key:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a piece of text using Groq API"""
        if not self.client:
            return [0.0] * 384
            
        try:
            # We use standard HTTP requests as the groq python client might not fully support embeddings yet depending on the version
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": text,
                "model": self.model_name
            }
            response = requests.post("https://api.groq.com/openai/v1/embeddings", headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["embedding"]
            
            print(f"Groq embedding failed, falling back. Response: {response.text}")
            return [0.0] * 384
        except Exception as e:
            print(f"ERROR: Groq embeddings failed: {e}")
            return [0.0] * 384

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks"""
        if not self.client:
            return [[0.0] * 384 for _ in texts]
            
        embeddings = []
        for text in texts:
            # Simple sequential for now since Groq is fast, or we could use asyncio.gather
            emb = await self.generate_embedding(text)
            embeddings.append(emb)
            await asyncio.sleep(0.1) # rate limit prevention

        return embeddings

# Singleton instance
embedding_service = EmbeddingService()
