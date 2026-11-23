import os, hashlib, math, sys
os.environ.update(JWT_SECRET="test-secret", DATABASE_URL="postgresql://postgres:pw@localhost:5432/devhive",
                  GROQ_API_KEY="x", HUGGINGFACE_API_KEY="x")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend"))
from fastapi.testclient import TestClient
from sqlalchemy import text

def fake_vec(s):
    v = [0.0]*384
    for w in s.lower().split():
        h = int(hashlib.md5(w.encode()).hexdigest(), 16)
        v[h % 384] += 1.0
    n = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x/n for x in v]

from api.services import embedding_service as es
async def fake_post(self, client, inputs):
    if os.environ.get("FAIL_EMB"): raise es.EmbeddingError("HTTP 410: api-inference retired")
    return [fake_vec(t) for t in inputs] if isinstance(inputs, list) else [fake_vec(inputs)]
es.EmbeddingService._post = fake_post

used = {}
import api.routers.search as sr
class FakeGroq:
    class chat:
        class completions:
            @staticmethod
            def create(model, messages):
                used["model"] = model
                class M: content = "Deploy with Vercel."
                class C: message = M
                class R: choices = [C]
                return R
sr._groq_client = lambda: FakeGroq

from api._app import app
from api.database import engine
with engine.begin() as c:
    c.execute(text("DROP TABLE IF EXISTS document_chunks, documents, users CASCADE"))

c = TestClient(app, follow_redirects=False)
ok = lambda name, cond, extra="": print(("PASS" if cond else "FAIL"), name, extra)

ok("search unauthenticated -> 401", c.post("/api/search", json={"query": "x"}).status_code == 401)
r = c.post("/api/auth/register", json={"email": "New@Test.com", "password": "password123", "full_name": "Nan"})
ok("register", r.status_code == 200, r.text[:80]); tok = r.json()["token"]
ok("register duplicate -> 400", c.post("/api/auth/register", json={"email": "new@test.com", "password": "password123", "full_name": "x"}).status_code == 400)
r = c.post("/api/auth/login", json={"email": "new@test.com", "password": "password123"})
ok("login (DB user, case-insensitive email)", r.status_code == 200)
ok("login wrong pw -> 401", c.post("/api/auth/login", json={"email": "new@test.com", "password": "nope"}).status_code == 401)
ok("login demo admin", c.post("/api/auth/login", json={"email": "admin@devhive.ai", "password": "admin123"}).status_code == 200)
admin = c.post("/api/auth/login", json={"email": "admin@devhive.ai", "password": "admin123"}).json()["token"]

H = {"Cookie": f"auth-token={tok}"}
body = b"Vercel deployment guide. Deploy the frontend with vercel and set environment variables.\n" * 3 + b"Database schema: users table has email and password hash columns."
r = c.post("/api/ingest?is_private=false", files={"file": ("guide.txt", body)}, headers=H)
ok("ingest txt", r.status_code == 200 and r.json()["status"] == "complete", r.text[:140])
r = c.post("/api/ingest", files={"file": ("guide.txt", body)}, headers=H)
ok("ingest duplicate filename", r.json().get("status") == "duplicate")

r = c.get("/api/documents", headers=H)
ok("GET /api/documents (no redirect)", r.status_code == 200 and r.json()["documents"][0]["status"] == "complete", str(r.status_code))
r = c.post("/api/search", json={"query": "how to deploy with vercel", "top_k": 5, "min_similarity": 0.1}, headers=H)
j = r.json()
ok("POST /api/search (no redirect)", r.status_code == 200 and len(j["chunks"]) > 0, str(r.status_code))
ok("search returns AI answer + model", j.get("ai_answer") == "Deploy with Vercel." and used.get("model") == "openai/gpt-oss-20b", str(used))
print("   top similarity:", round(j["chunks"][0]["similarity"], 3))

doc_id = c.get("/api/documents", headers=H).json()["documents"][0]["id"]
ok("delete as employee -> 403", c.delete(f"/api/documents/{doc_id}", headers=H).status_code == 403)
ok("delete as admin", c.delete(f"/api/documents/{doc_id}", headers={"Cookie": f"auth-token={admin}"}).status_code == 200)

os.environ["FAIL_EMB"] = "1"
r = c.post("/api/ingest", files={"file": ("other.txt", b"some different words here")}, headers=H)
ok("embedding failure -> loud 502, not silent", r.status_code == 502, r.text[:120])
st = c.get("/api/documents", headers=H).json()["documents"]
ok("failed doc status = failed (not stuck 'processing')", st and st[0]["status"] == "failed", str(st))
r = c.post("/api/search", json={"query": "x"}, headers=H)
ok("search with embedding outage -> 502 with message", r.status_code == 502, r.text[:100])

# prove the original failure mode: zero vector => NaN distance => nothing ever passes the similarity filter
with engine.connect() as conn:
    row = conn.execute(text("SELECT 1 - ('[1,0,0]'::vector <=> '[0,0,0]'::vector) AS s")).fetchone()
    print("   old behaviour: similarity vs zero vector =", row.s, "(NaN >= 0.3 is", float(row.s) >= 0.3, ")")
