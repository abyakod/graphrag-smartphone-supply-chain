"""
PhoneGraph: FastAPI Application

Main application entry point. Configures CORS, includes all
route modules, and provides health check endpoint.

Run with: uvicorn api.main:app --host 0.0.0.0 --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.models import HealthResponse
from api.routes import query, simulate, insights, graph
from graph.connection import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-20s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    logger.info("🚀 PhoneGraph API starting up...")
    
    # Verify Memgraph connection
    try:
        conn = get_connection()
        health = conn.health_check()
        logger.info(f"✅ Memgraph connected: {health.get('node_count', 0)} nodes, "
                    f"{health.get('edge_count', 0)} edges")
    except Exception as e:
        logger.warning(f"⚠️ Memgraph not ready: {e} — API will start anyway")
    
    yield
    
    logger.info("👋 PhoneGraph API shutting down")


app = FastAPI(
    title="PhoneGraph API",
    description=(
        "**Smartphone Supply Chain Intelligence Engine**\n\n"
        "Query the global smartphone supply chain knowledge graph using "
        "GraphRAG. Simulate disruptions and discover hidden dependencies.\n\n"
        "Built with Memgraph + LangChain + GPT-4o-mini."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(query.router, tags=["Query"])
app.include_router(simulate.router, tags=["Simulation"])
app.include_router(insights.router, tags=["Insights"])
app.include_router(graph.router, tags=["Graph"])


@app.get("/", summary="Root", include_in_schema=False)
async def root() -> Dict[str, str]:
    """Redirect to docs."""
    return {
        "message": "PhoneGraph API v1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API and Memgraph connectivity.",
    tags=["System"],
)
async def health_check() -> Dict[str, Any]:
    """API + Memgraph health check."""
    try:
        conn = get_connection()
        health = conn.health_check()
        
        # Get graph stats
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
            "status": "healthy",
            "memgraph_connected": True,
            "graph_stats": {
                "total_nodes": total_nodes_r[0]["count"] if total_nodes_r else 0,
                "total_edges": total_edges_r[0]["count"] if total_edges_r else 0,
                "node_counts": {r["label"]: r["count"] for r in label_counts},
                "relationship_counts": {r["type"]: r["count"] for r in rel_counts},
            },
            "version": "1.0.0",
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "memgraph_connected": False,
            "graph_stats": None,
            "version": "1.0.0",
        }
