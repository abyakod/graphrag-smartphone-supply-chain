"""
PhoneGraph: Graph Route

GET /graph — Returns graph statistics and subgraph data for visualization.
GET /graph/path — Find shortest path between two nodes.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from api.models import GraphStats, PathRequest, PathResponse
from graph.connection import get_connection
from graph.algorithms import find_shortest_path, get_subgraph

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/graph/stats",
    response_model=GraphStats,
    summary="Graph statistics",
    description="Returns counts of nodes and relationships in the knowledge graph.",
)
async def graph_stats() -> Dict[str, Any]:
    """Get graph node and relationship counts."""
    conn = get_connection()
    
    try:
        total_nodes_r = conn.execute_and_fetch(
            "MATCH (n) RETURN count(n) AS count"
        )
        total_edges_r = conn.execute_and_fetch(
            "MATCH ()-[r]->() RETURN count(r) AS count"
        )
        
        label_counts = conn.execute_and_fetch(
            "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count"
        )
        rel_counts = conn.execute_and_fetch(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count"
        )
        
        return {
            "total_nodes": total_nodes_r[0]["count"] if total_nodes_r else 0,
            "total_edges": total_edges_r[0]["count"] if total_edges_r else 0,
            "node_counts": {r["label"]: r["count"] for r in label_counts},
            "relationship_counts": {r["type"]: r["count"] for r in rel_counts},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/graph/subgraph",
    summary="Get subgraph around a node",
    description="Returns nodes and edges within N hops of a given node.",
)
async def subgraph(
    node_name: str = Query(..., description="Name of center node"),
    hops: int = Query(default=2, ge=1, le=4, description="Number of hops"),
) -> Dict[str, Any]:
    """Get a subgraph centered on a node."""
    try:
        result = get_subgraph(node_name, hops)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/graph/path",
    response_model=PathResponse,
    summary="Find shortest path",
    description="Find the shortest supply chain path between two nodes.",
)
async def shortest_path(request: PathRequest) -> Dict[str, Any]:
    """Find shortest path between two nodes."""
    try:
        result = find_shortest_path(request.start, request.end)
        
        if result:
            return {
                "start": request.start,
                "end": request.end,
                "found": True,
                **result,
            }
        
        return {
            "start": request.start,
            "end": request.end,
            "found": False,
            "hops": 0,
            "supply_chain": [],
            "node_types": [],
            "relationship_types": [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/graph/nodes",
    summary="List all nodes of a type",
    description="Returns all nodes of a given label type.",
)
async def list_nodes(
    label: str = Query(
        default="Material",
        description="Node label: Material, Company, Component, Device, Country, RiskEvent, Regulation",
    ),
    limit: int = Query(default=50, ge=1, le=200),
) -> List[Dict[str, Any]]:
    """List all nodes of a given type."""
    conn = get_connection()
    
    valid_labels = [
        "Material", "Company", "Component", "Device",
        "Country", "RiskEvent", "Regulation",
    ]
    
    if label not in valid_labels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid label. Must be one of: {valid_labels}",
        )
    
    try:
        results = conn.execute_and_fetch(
            f"MATCH (n:{label}) RETURN properties(n) AS props "
            f"ORDER BY n.name LIMIT {limit}"
        )
        return [r["props"] for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
