"""
PhoneGraph: Query Route

POST /query — Ask a natural language question about the supply chain.
Supports GraphRAG mode, Vanilla RAG mode, or comparison mode.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from api.models import CompareResponse, QueryRequest, QueryResponse
from graphrag.chain import get_rag

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/query",
    response_model=None,
    summary="Ask a supply chain question",
    description="Query the PhoneGraph knowledge graph using GraphRAG. "
                "Supports 'graphrag', 'vanilla_rag', or 'compare' modes.",
)
async def query(request: QueryRequest) -> Dict[str, Any]:
    """
    Execute a natural language query against the supply chain graph.
    
    - **question**: Your question (e.g., "What happens if TSMC shuts down?")
    - **mode**: 'graphrag' (default) or 'vanilla_rag'
    - **compare**: If true, runs both modes and shows comparison
    """
    try:
        rag = get_rag()
        
        if request.compare:
            result = rag.compare(request.question)
            return result
        elif request.mode == "vanilla_rag":
            result = rag.vanilla_rag_query(request.question)
            return result
        else:
            result = rag.query(request.question)
            return result
    
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
