from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/dashboard")
async def get_neural_analytics() -> Dict[str, Any]:
    """
    Returns analytics data for the Neural Analytics Dashboard:
    - Query velocity (queries over 30 days)
    - Confidence scores
    - Top search terms
    """
    # Placeholder data for the frontend charts. 
    # In a fully integrated system, this would aggregate real DB logs.
    return {
        "query_velocity": [
            {"day": "Day 1", "queries": 12},
            {"day": "Day 5", "queries": 45},
            {"day": "Day 10", "queries": 23},
            {"day": "Day 15", "queries": 78},
            {"day": "Day 20", "queries": 105},
            {"day": "Day 25", "queries": 90},
            {"day": "Day 30", "queries": 134},
        ],
        "confidence_scores": [
            {"name": "High (>0.9)", "value": 400},
            {"name": "Medium (0.7-0.9)", "value": 300},
            {"name": "Low (<0.7)", "value": 100},
        ],
        "top_terms": [
            {"term": "authentication flow", "count": 150},
            {"term": "database schema", "count": 120},
            {"term": "vercel deployment", "count": 80},
            {"term": "api keys", "count": 65},
            {"term": "background tasks", "count": 45},
        ]
    }
