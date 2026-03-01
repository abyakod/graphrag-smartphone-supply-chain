"""
PhoneGraph: Pydantic Request/Response Models

Type-safe API models for the FastAPI backend.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════
# Request Models
# ═══════════════════════════════════════════════════

class QueryRequest(BaseModel):
    """GraphRAG query request."""
    question: str = Field(..., description="Natural language question", min_length=5)
    mode: str = Field(
        default="graphrag",
        description="Query mode: 'graphrag' or 'vanilla_rag'",
    )
    compare: bool = Field(
        default=False,
        description="If true, run both modes and compare results",
    )


class SimulateRequest(BaseModel):
    """Supply chain shock simulation request."""
    disrupted_node: str = Field(
        ..., description="Name of the disrupted node (e.g., 'Gallium', 'TSMC')"
    )
    node_type: str = Field(
        default="Material",
        description="Type: 'Material', 'Company', or 'Country'",
    )
    severity: int = Field(
        default=8,
        description="Disruption severity (1-10)",
        ge=1,
        le=10,
    )


class PathRequest(BaseModel):
    """Shortest path request."""
    start: str = Field(..., description="Start node name")
    end: str = Field(..., description="End node name")


# ═══════════════════════════════════════════════════
# Response Models
# ═══════════════════════════════════════════════════

class QueryResponse(BaseModel):
    """GraphRAG query response."""
    question: str
    answer: str
    mode: str
    cypher_query: Optional[str] = None
    nodes_traversed: int = 0
    hops: int = 0
    confidence: float = 0.0
    sources: List[str] = []
    reasoning_chain: List[str] = []


class CompareResponse(BaseModel):
    """Comparison of GraphRAG vs Vanilla RAG."""
    question: str
    graphrag_answer: str
    vanilla_rag_answer: str
    graphrag_hops: int
    vanilla_rag_hops: int
    graphrag_nodes: int
    vanilla_rag_nodes: int
    graphrag_confidence: float
    vanilla_rag_confidence: float
    winner: str
    why_graphrag_wins: str


class DeviceImpact(BaseModel):
    """Impact on a single device from a shock event."""
    device: str
    brand: str = ""
    current_price_usd: float = 0
    impact_score: float = 0
    price_increase_usd: float = 0
    price_increase_pct: float = 0
    recovery_months: int = 0
    affected_components: List[str] = []
    single_source_risk: bool = False
    units_sold_millions: float = 0


class SimulateResponse(BaseModel):
    """Shock simulation response."""
    disrupted_node: str
    node_type: str
    severity: int
    affected_devices: List[DeviceImpact] = []
    total_price_impact_usd: float = 0
    total_market_impact_usd_billions: float = 0
    most_vulnerable: str = ""
    ripple_path: List[str] = []
    recovery_estimate_months: int = 0
    devices_affected_count: int = 0


class AlgorithmResult(BaseModel):
    """Graph algorithm result."""
    name: str
    type: str = ""
    rank: Optional[float] = None
    betweenness_centrality: Optional[float] = None
    community_id: Optional[int] = None


class InsightResponse(BaseModel):
    """Precomputed supply chain insight."""
    title: str
    description: str
    metric_value: str
    metric_label: str
    category: str
    severity: str = "info"


class GraphStats(BaseModel):
    """Graph statistics response."""
    total_nodes: int
    total_edges: int
    node_counts: Dict[str, int] = {}
    relationship_counts: Dict[str, int] = {}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    memgraph_connected: bool
    graph_stats: Optional[GraphStats] = None
    version: str = "1.0.0"


class PathResponse(BaseModel):
    """Shortest path response."""
    start: str
    end: str
    hops: int = 0
    supply_chain: List[str] = []
    node_types: List[str] = []
    relationship_types: List[str] = []
    found: bool = False
