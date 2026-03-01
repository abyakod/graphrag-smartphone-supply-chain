"""
PhoneGraph: Simulate Route

POST /simulate — Simulate a supply chain disruption scenario.
Returns affected devices, price impacts, and recovery estimates.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from api.models import SimulateRequest, SimulateResponse
from algorithms.risk_scoring import simulate_supply_shock

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/simulate",
    response_model=SimulateResponse,
    summary="Simulate supply chain shock",
    description="Simulate a disruption to a material, company, or country "
                "and see the ripple effects across the smartphone supply chain.",
)
async def simulate(request: SimulateRequest) -> Dict[str, Any]:
    """
    Simulate a supply chain shock event.
    
    - **disrupted_node**: Name of disrupted entity (e.g., "Gallium", "TSMC", "Taiwan")
    - **node_type**: Entity type: "Material", "Company", or "Country"
    - **severity**: Disruption severity 1-10
    """
    try:
        result = simulate_supply_shock(
            disrupted_node=request.disrupted_node,
            node_type=request.node_type,
            severity=request.severity,
        )
        return result
    
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
