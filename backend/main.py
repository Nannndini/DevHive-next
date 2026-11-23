"""Local dev shim: runs the exact same app Vercel deploys (frontend/api/_app.py).

    cd backend && uvicorn main:app --reload --port 8000
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "frontend"))

from api._app import app  # noqa: E402,F401
