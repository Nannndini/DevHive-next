import hashlib
import re
from sentence_transformers import SentenceTransformer
from groq import Groq
from database import supabase
from config import settings

# Load model once at startup
_model = None
_groq = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_groq():
    global _groq
    if _groq is None:
        _groq = Groq(api_key=settings.groq_api_key)
    return _groq

def embed_text(text: str) -> list[float]:
    return get_model().encode(text).tolist()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for better context."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 20]

def get_content_hash(content: str) -> str:
    return hashlib.md5(content.strip().lower().encode()).hexdigest()

def store_document_with_embeddings(
    user_id: str,
    title: str,
    content: str,
    source: str = "upload",
    file_type: str = "txt",
    metadata: dict = {}
) -> dict:
    """Full pipeline: hash check → store doc → embed chunks → store embeddings."""
    content_hash = get_content_hash(content)

    # Deduplication check
    existing = supabase.table("documents").select("id, title").eq("content_hash", content_hash).execute()
    if existing.data:
        return {"duplicate": True, "existing_id": existing.data[0]["id"], "title": existing.data[0]["title"]}

    # Store document
    doc = supabase.table("documents").insert({
        "user_id": user_id,
        "title": title,
        "content": content,
        "source": source,
        "file_type": file_type,
        "content_hash": content_hash,
        "metadata": metadata
    }).execute()

    doc_id = doc.data[0]["id"]

    # Chunk and embed
    chunks = chunk_text(content)
    embeddings_data = []
    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        embeddings_data.append({
            "document_id": doc_id,
            "chunk_index": i,
            "chunk_text": chunk,
            "embedding": embedding
        })

    # Batch insert embeddings
    if embeddings_data:
        supabase.table("embeddings").insert(embeddings_data).execute()

    return {"duplicate": False, "document_id": doc_id, "chunks": len(chunks)}

def semantic_search(query: str, limit: int = 5, threshold: float = 0.3) -> list[dict]:
    """Search using pgvector cosine similarity."""
    query_embedding = embed_text(query)
    result = supabase.rpc("match_embeddings", {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": limit
    }).execute()
    return result.data or []

def answer_question(question: str, user_id: str) -> dict:
    """RAG: retrieve context → generate answer with Groq LLaMA."""
    # 1. Retrieve relevant chunks
    results = semantic_search(question, limit=5)

    if not results:
        return {
            "answer": "I couldn't find relevant information in the knowledge base. Please upload more documents.",
            "sources": [],
            "question": question
        }

    # 2. Build context
    context_parts = []
    sources = []
    for r in results:
        context_parts.append(f"[Source: {r['title']}]\n{r['chunk_text']}")
        if r["title"] not in [s["title"] for s in sources]:
            sources.append({"title": r["title"], "source": r["source"], "similarity": round(r["similarity"], 3)})

    context = "\n\n".join(context_parts)

    # 3. Generate answer with Groq LLaMA
    prompt = f"""You are a helpful knowledge assistant. Answer the question using ONLY the provided context.
If the context doesn't contain enough information, say so clearly.

Context:
{context}

Question: {question}

Provide a clear, structured answer. Cite which documents you used."""

    response = get_groq().chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.3
    )

    answer = response.choices[0].message.content

    # 4. Log Q&A
    try:
        supabase.table("qa_logs").insert({
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "sources": sources
        }).execute()
    except:
        pass

    return {"answer": answer, "sources": sources, "question": question}
