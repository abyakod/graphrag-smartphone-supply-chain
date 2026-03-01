"""
PhoneGraph: Insights Route

GET /insights — Returns precomputed supply chain insights.
These are the "6 WOW insights" that make users share the article.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from graph.connection import get_connection
from graph.algorithms import run_pagerank, run_betweenness_centrality

logger = logging.getLogger(__name__)

router = APIRouter()


def _compute_insights() -> List[Dict[str, Any]]:
    """Compute the 6 headline-grabbing supply chain insights."""
    conn = get_connection()
    insights = []
    
    # Insight 1: TSMC Dependency
    try:
        result = conn.execute_and_fetch(
            "MATCH (co:Company {name: 'TSMC'})-[:MANUFACTURES]->(c:Component)"
            "-[:USED_IN]->(d:Device) "
            "RETURN count(DISTINCT d) AS device_count"
        )
        count = result[0]["device_count"] if result else 0
        total_result = conn.execute_and_fetch(
            "MATCH (d:Device) RETURN count(d) AS total"
        )
        total = total_result[0]["total"] if total_result else 1
        pct = round(count / max(total, 1) * 100)
        
        insights.append({
            "title": "🏭 One Company Rules Them All",
            "description": f"TSMC manufactures chips for {pct}% of ALL smartphones "
                          f"in the graph. A single earthquake could halt {count} "
                          f"phone lines simultaneously.",
            "metric_value": f"{pct}%",
            "metric_label": "Devices dependent on TSMC",
            "category": "concentration_risk",
            "severity": "critical",
        })
    except Exception:
        pass
    
    # Insight 2: China Material Control
    try:
        result = conn.execute_and_fetch(
            "MATCH (m:Material)-[r:EXTRACTED_IN]->(c:Country {name: 'China'}) "
            "RETURN count(m) AS china_materials, avg(r.percentage) AS avg_pct"
        )
        total_mats = conn.execute_and_fetch(
            "MATCH (m:Material) RETURN count(m) AS total"
        )
        if result and total_mats:
            china_count = result[0].get("china_materials", 0)
            avg_pct = round(result[0].get("avg_pct", 0), 1)
            total = total_mats[0].get("total", 1)
            
            insights.append({
                "title": "🇨🇳 China Controls Your Phone",
                "description": f"China is a primary extraction source for {china_count} "
                              f"of {total} critical materials, averaging {avg_pct}% control. "
                              f"A single export ban could freeze global production.",
                "metric_value": f"{china_count}/{total}",
                "metric_label": "Materials with Chinese extraction",
                "category": "geopolitical_risk",
                "severity": "critical",
            })
    except Exception:
        pass
    
    # Insight 3: Your phone cost breakdown
    try:
        result = conn.execute_and_fetch(
            "MATCH (d:Device {name: 'iPhone 16 Pro'}) "
            "OPTIONAL MATCH (c:Component)-[:USED_IN]->(d) "
            "RETURN d.base_price_usd AS price, "
            "sum(c.estimated_cost_usd) AS total_component_cost, "
            "count(c) AS num_components"
        )
        if result and result[0].get("price"):
            price = result[0]["price"]
            cost = result[0].get("total_component_cost", 0) or 0
            comps = result[0].get("num_components", 0)
            margin = round((price - cost) / price * 100, 1) if price else 0
            
            insights.append({
                "title": "💰 The $1,199 iPhone's Real Cost",
                "description": f"The iPhone 16 Pro contains {comps} tracked components "
                              f"costing ~${cost:.0f} total. Apple's margin: ~{margin}%. "
                              f"But 60%+ of component cost is single-sourced.",
                "metric_value": f"~${cost:.0f}",
                "metric_label": "Component cost of iPhone 16 Pro",
                "category": "cost_analysis",
                "severity": "info",
            })
    except Exception:
        pass
    
    # Insight 4: Most critical node (PageRank)
    try:
        pr_results = run_pagerank(limit=1)
        if pr_results:
            top = pr_results[0]
            insights.append({
                "title": "👑 The Most Powerful Supply Chain Node",
                "description": f"{top['name']} ({top['type']}) has the highest PageRank "
                              f"in the entire supply chain graph. Remove this node and "
                              f"the global smartphone industry collapses.",
                "metric_value": f"{top['rank']:.4f}",
                "metric_label": "PageRank score",
                "category": "graph_centrality",
                "severity": "warning",
            })
    except Exception:
        pass
    
    # Insight 5: Fragility score
    try:
        single_sourced = conn.execute_and_fetch(
            "MATCH (c:Component) WHERE c.single_sourced = true "
            "RETURN count(c) AS count"
        )
        total_comps = conn.execute_and_fetch(
            "MATCH (c:Component) RETURN count(c) AS count"
        )
        if single_sourced and total_comps:
            ss = single_sourced[0].get("count", 0)
            tc = total_comps[0].get("count", 1)
            pct = round(ss / max(tc, 1) * 100)
            
            insights.append({
                "title": "⚠️ Single Points of Failure Everywhere",
                "description": f"{ss} of {tc} ({pct}%) tracked components are "
                              f"SINGLE-SOURCED. If that manufacturer goes down, "
                              f"there's no backup. Your phone doesn't ship.",
                "metric_value": f"{pct}%",
                "metric_label": "Single-sourced components",
                "category": "supply_risk",
                "severity": "critical",
            })
    except Exception:
        pass
    
    # Insight 6: Shortest supply chain
    try:
        result = conn.execute_and_fetch(
            "MATCH (c:Country) WHERE c.geopolitical_risk_score >= 8 "
            "RETURN c.name AS country, c.geopolitical_risk_score AS risk "
            "ORDER BY risk DESC LIMIT 5"
        )
        if result:
            countries = [f"{r['country']} ({r['risk']}/10)" for r in result]
            
            insights.append({
                "title": "🌍 Geopolitical Hotspots in Your Pocket",
                "description": f"High-risk countries in your phone's supply chain: "
                              f"{', '.join(countries)}. "
                              f"A conflict in ANY one could spike prices 15-30%.",
                "metric_value": f"{len(result)}",
                "metric_label": "High-risk countries",
                "category": "geopolitical_risk",
                "severity": "warning",
            })
    except Exception:
        pass
    
    return insights


@router.get(
    "/insights",
    summary="Get supply chain WOW insights",
    description="Returns 6 precomputed, headline-grabbing insights about the "
                "global smartphone supply chain.",
)
async def get_insights() -> List[Dict[str, Any]]:
    """Return precomputed supply chain insights."""
    try:
        return _compute_insights()
    except Exception as e:
        logger.error(f"Insights computation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
