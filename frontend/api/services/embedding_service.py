import os
import asyncio
import logging
from typing import List

import httpx

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384  # BAAI/bge-small-en-v1.5


class EmbeddingError(RuntimeError):
    """Raised when embeddings cannot be generated. Never swallowed into fake vectors."""


class EmbeddingService:
    """Embeddings via the Hugging Face Inference router (api-inference.huggingface.co is retired)."""

    def __init__(self):
        self.model_name = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        self.api_url = (
            "https://router.huggingface.co/hf-inference/models/"
            f"{self.model_name}/pipeline/feature-extraction"
        )

    @property
    def _headers(self) -> dict:
        key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
        if not key:
            raise EmbeddingError("HUGGINGFACE_API_KEY is not set")
        return {"Authorization": f"Bearer {key}"}

    async def _post(self, client: httpx.AsyncClient, inputs) -> list:
        last = "unknown error"
        for attempt in range(3):
            try:
                resp = await client.post(
                    self.api_url,
                    headers=self._headers,
                    json={"inputs": inputs, "options": {"wait_for_model": True}},
                )
            except httpx.HTTPError as e:
                last = f"network error: {e}"
            else:
                if resp.status_code == 200:
                    return resp.json()
                last = f"HTTP {resp.status_code}: {resp.text[:200]}"
                if resp.status_code not in (429, 500, 502, 503, 504):
                    break  # 401/403/404 etc. will not fix themselves
            await asyncio.sleep(2 ** attempt)
        raise EmbeddingError(f"Hugging Face embedding request failed ({last})")

    @staticmethod
    def _validate(vec) -> List[float]:
        if not (isinstance(vec, list) and len(vec) == EMBEDDING_DIM and isinstance(vec[0], (int, float))):
            raise EmbeddingError(f"Unexpected embedding shape (expected {EMBEDDING_DIM} floats)")
        if not any(vec):
            raise EmbeddingError("Received an all-zero embedding")
        return vec

    async def generate_embedding(self, text: str) -> List[float]:
        async with httpx.AsyncClient(timeout=30) as client:
            result = await self._post(client, text)
        if isinstance(result, list) and result and isinstance(result[0], list):
            result = result[0]
        return self._validate(result)

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        out: List[List[float]] = []
        async with httpx.AsyncClient(timeout=60) as client:
            for i in range(0, len(texts), 10):
                batch = texts[i:i + 10]
                result = await self._post(client, batch)
                if not (isinstance(result, list) and len(result) == len(batch)):
                    raise EmbeddingError("Embedding batch size mismatch")
                out.extend(self._validate(v) for v in result)
        return out


embedding_service = EmbeddingService()
