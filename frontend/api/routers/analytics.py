from fastapi import APIRouter, Depends
from typing import Dict, Any
from api.auth import RoleChecker

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)

@router.get("/dashboard")
async def get_neural_analytics(user: dict = Depends(RoleChecker(["admin", "manager"]))) -> Dict[str, Any]:
    """
    Returns analytics data for the Neural Analytics Dashboard:
    - Query velocity (queries over 30 days)
    - Confidence scores
    - Top search terms
    """
    # Placeholder data for the frontend charts. 
    # In a fully integrated system, this would aggregate real DB logs.
    return {
        "stats": {
            "total_queries": 92,
            "avg_confidence": "85%",
            "active_users": 6,
            "system_latency": "1.2s"
        },
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
        ]
    }

@router.get("/overview")
async def get_system_overview(user: dict = Depends(RoleChecker(["admin", "manager"]))) -> Dict[str, Any]:
    """
    Returns data for the System Overview dashboard.
    """
    return {
        "stats": {
            "total_documents": 14,
            "total_chunks": 620,
            "active_users": 6,
            "uptime_percentage": "99.99%"
        },
        "documents": [
            {"id": 1, "name": "core_sys_config.md", "status": "INDEXED", "chunks": 45},
            {"id": 2, "name": "team_directory.txt", "status": "VECTOR_SYNC", "chunks": 12},
            {"id": 3, "name": "q3_financial_report.pdf", "status": "STAGED", "chunks": 156},
            {"id": 4, "name": "api_documentation_v2.md", "status": "INDEXED", "chunks": 89}
        ],
        "recent_queries": [
            {"id": 101, "query": "How to deploy to vercel?", "response_time": "1.2s", "chunks_used": 4, "timestamp": "2 mins ago"},
            {"id": 102, "query": "What is the database schema for users?", "response_time": "0.8s", "chunks_used": 2, "timestamp": "15 mins ago"},
            {"id": 103, "query": "Show me the authentication flow", "response_time": "2.1s", "chunks_used": 8, "timestamp": "1 hour ago"},
            {"id": 104, "query": "List all active background workers", "response_time": "1.5s", "chunks_used": 5, "timestamp": "3 hours ago"}
        ]
    }
