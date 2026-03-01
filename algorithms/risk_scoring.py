"""
PhoneGraph: Risk Scoring & Supply Chain Shock Simulator

The VIRAL feature: User picks any material, company, or country.
System shows the ripple effect across the entire supply chain
with estimated price impacts on every affected device.

Run standalone: python -m algorithms.risk_scoring
"""

import logging
from typing import Any, Dict, List

from graph.connection import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def simulate_supply_shock(
    disrupted_node: str,
    node_type: str = "Material",
    severity: int = 8,
) -> Dict[str, Any]:
    """
    Simulate a supply chain shock and calculate ripple effects.
    
    Traverses outward from the disrupted node up to 6 hops.
    Calculates impact on each device based on:
    - Hops from disruption (closer = more impact)
    - Single-source dependency (True = 3x multiplier)
    - Severity of the disruption
    
    Args:
        disrupted_node: Name of the disrupted node
        node_type: Type of node (Material, Company, Country)
        severity: Disruption severity (1-10)
        
    Returns:
        Dict with affected_devices, total_market_impact,
        most_vulnerable, ripple_path
    """
    conn = get_connection()
    logger.info(f"⚡ Simulating shock: {disrupted_node} "
                f"(type={node_type}, severity={severity})")
    
    affected_devices = []
    
    # Strategy 1: Direct material → component → device path
    if node_type == "Material":
        affected_devices = _shock_from_material(conn, disrupted_node, severity)
    elif node_type == "Company":
        affected_devices = _shock_from_company(conn, disrupted_node, severity)
    elif node_type == "Country":
        affected_devices = _shock_from_country(conn, disrupted_node, severity)
    
    # If no results from specific queries, try generic traversal
    if not affected_devices:
        affected_devices = _shock_generic(conn, disrupted_node, severity)
    
    # Calculate totals
    total_impact = sum(d.get("price_increase_usd", 0) for d in affected_devices)
    total_market_impact = sum(
        d.get("price_increase_usd", 0) * d.get("units_sold_millions", 1)
        for d in affected_devices
    ) / 1000  # Convert to billions
    
    most_vulnerable = (
        affected_devices[0]["device"] if affected_devices else "None"
    )
    
    # Build ripple path
    ripple_path = _build_ripple_path(conn, disrupted_node, node_type)
    
    result = {
        "disrupted_node": disrupted_node,
        "node_type": node_type,
        "severity": severity,
        "affected_devices": affected_devices,
        "total_price_impact_usd": round(total_impact, 2),
        "total_market_impact_usd_billions": round(total_market_impact, 2),
        "most_vulnerable": most_vulnerable,
        "ripple_path": ripple_path,
        "recovery_estimate_months": _estimate_recovery(severity, node_type),
        "devices_affected_count": len(affected_devices),
    }
    
    logger.info(f"  📊 {len(affected_devices)} devices affected, "
                f"total impact: ${total_impact:.2f}")
    
    return result


def _shock_from_material(
    conn, material_name: str, severity: int
) -> List[Dict[str, Any]]:
    """Calculate device impact from a material disruption."""
    query = """
    MATCH (m:Material {name: $name})-[:REQUIRED_FOR]->(comp:Component)-[:USED_IN]->(d:Device)
    OPTIONAL MATCH (co:Company)-[:MANUFACTURES]->(comp)
    WITH d, comp, co,
         comp.single_sourced AS single_sourced,
         comp.estimated_cost_usd AS component_cost,
         d.base_price_usd AS device_price,
         d.units_sold_millions AS units_sold
    RETURN DISTINCT
        d.name AS device,
        d.brand AS brand,
        device_price,
        units_sold,
        collect(DISTINCT comp.name) AS affected_components,
        collect(DISTINCT co.name) AS affected_manufacturers,
        CASE WHEN any(ss IN collect(single_sourced) WHERE ss = true)
             THEN true ELSE false END AS has_single_source
    """
    
    try:
        results = list(conn.db.execute_and_fetch(query, {"name": material_name}))
    except Exception:
        # Fallback without parameters
        escaped = material_name.replace("'", "\\'")
        fallback_query = f"""
        MATCH (m:Material {{name: '{escaped}'}})-[:REQUIRED_FOR]->(comp:Component)-[:USED_IN]->(d:Device)
        OPTIONAL MATCH (co:Company)-[:MANUFACTURES]->(comp)
        RETURN DISTINCT
            d.name AS device,
            d.brand AS brand,
            d.base_price_usd AS device_price,
            d.units_sold_millions AS units_sold,
            collect(DISTINCT comp.name) AS affected_components,
            collect(DISTINCT co.name) AS affected_manufacturers,
            comp.single_sourced AS has_single_source
        """
        results = conn.execute_and_fetch(fallback_query)
    
    devices = []
    for r in results:
        device_price = r.get("device_price", 0) or 0
        single_source_multiplier = 3.0 if r.get("has_single_source") else 1.0
        base_impact = device_price * (severity / 100.0) * single_source_multiplier
        price_increase = min(base_impact, device_price * 0.3)  # Cap at 30%
        
        devices.append({
            "device": r["device"],
            "brand": r.get("brand", ""),
            "current_price_usd": device_price,
            "impact_score": round(severity * single_source_multiplier / 10, 2),
            "price_increase_usd": round(price_increase, 2),
            "price_increase_pct": round(price_increase / device_price * 100, 1) if device_price else 0,
            "recovery_months": _estimate_recovery(severity, "Material"),
            "affected_components": r.get("affected_components", []),
            "single_source_risk": bool(r.get("has_single_source")),
            "units_sold_millions": r.get("units_sold", 0) or 0,
        })
    
    devices.sort(key=lambda x: x["price_increase_usd"], reverse=True)
    return devices


def _shock_from_company(
    conn, company_name: str, severity: int
) -> List[Dict[str, Any]]:
    """Calculate device impact from a company disruption."""
    escaped = company_name.replace("'", "\\'")
    query = f"""
    MATCH (co:Company {{name: '{escaped}'}})-[:MANUFACTURES]->(comp:Component)-[:USED_IN]->(d:Device)
    RETURN DISTINCT
        d.name AS device,
        d.brand AS brand,
        d.base_price_usd AS device_price,
        d.units_sold_millions AS units_sold,
        collect(DISTINCT comp.name) AS affected_components,
        comp.single_sourced AS single_sourced
    """
    
    results = conn.execute_and_fetch(query)
    
    devices = []
    for r in results:
        device_price = r.get("device_price", 0) or 0
        single_sourced = r.get("single_sourced", False)
        multiplier = 3.0 if single_sourced else 1.5
        price_increase = device_price * (severity / 80.0) * multiplier
        price_increase = min(price_increase, device_price * 0.4)
        
        devices.append({
            "device": r["device"],
            "brand": r.get("brand", ""),
            "current_price_usd": device_price,
            "impact_score": round(severity * multiplier / 10, 2),
            "price_increase_usd": round(price_increase, 2),
            "price_increase_pct": round(price_increase / device_price * 100, 1) if device_price else 0,
            "recovery_months": _estimate_recovery(severity, "Company"),
            "affected_components": r.get("affected_components", []),
            "single_source_risk": bool(single_sourced),
            "units_sold_millions": r.get("units_sold", 0) or 0,
        })
    
    # Also check SUPPLIES_TO relationships
    supply_query = f"""
    MATCH (co:Company {{name: '{escaped}'}})-[:SUPPLIES_TO]->(co2:Company)
    MATCH (co2)-[:MANUFACTURES|SUPPLIES_TO*1..2]->(comp:Component)-[:USED_IN]->(d:Device)
    RETURN DISTINCT
        d.name AS device,
        d.brand AS brand,
        d.base_price_usd AS device_price,
        d.units_sold_millions AS units_sold,
        co2.name AS via_company
    """
    
    try:
        supply_results = conn.execute_and_fetch(supply_query)
        existing_devices = {d["device"] for d in devices}
        
        for r in supply_results:
            if r["device"] not in existing_devices:
                device_price = r.get("device_price", 0) or 0
                price_increase = device_price * (severity / 120.0)
                
                devices.append({
                    "device": r["device"],
                    "brand": r.get("brand", ""),
                    "current_price_usd": device_price,
                    "impact_score": round(severity / 15, 2),
                    "price_increase_usd": round(price_increase, 2),
                    "price_increase_pct": round(price_increase / device_price * 100, 1) if device_price else 0,
                    "recovery_months": _estimate_recovery(severity, "Company") + 3,
                    "affected_components": [],
                    "single_source_risk": False,
                    "units_sold_millions": r.get("units_sold", 0) or 0,
                })
                existing_devices.add(r["device"])
    except Exception:
        pass
    
    devices.sort(key=lambda x: x["price_increase_usd"], reverse=True)
    return devices


def _shock_from_country(
    conn, country_name: str, severity: int
) -> List[Dict[str, Any]]:
    """Calculate device impact from a country disruption."""
    escaped = country_name.replace("'", "\\'")
    
    # Materials extracted in this country
    mat_query = f"""
    MATCH (m:Material)-[:EXTRACTED_IN]->(c:Country {{name: '{escaped}'}})
    MATCH (m)-[:REQUIRED_FOR]->(comp:Component)-[:USED_IN]->(d:Device)
    RETURN DISTINCT
        d.name AS device,
        d.brand AS brand,
        d.base_price_usd AS device_price,
        d.units_sold_millions AS units_sold,
        collect(DISTINCT m.name) AS affected_materials,
        collect(DISTINCT comp.name) AS affected_components
    """
    
    # Companies headquartered in this country
    comp_query = f"""
    MATCH (co:Company)-[:HEADQUARTERED_IN]->(c:Country {{name: '{escaped}'}})
    MATCH (co)-[:MANUFACTURES]->(comp:Component)-[:USED_IN]->(d:Device)
    RETURN DISTINCT
        d.name AS device,
        d.brand AS brand,
        d.base_price_usd AS device_price,
        d.units_sold_millions AS units_sold,
        collect(DISTINCT co.name) AS affected_companies,
        collect(DISTINCT comp.name) AS affected_components
    """
    
    devices = []
    existing = set()
    
    for query in [mat_query, comp_query]:
        try:
            results = conn.execute_and_fetch(query)
            for r in results:
                if r["device"] in existing:
                    continue
                existing.add(r["device"])
                
                device_price = r.get("device_price", 0) or 0
                price_increase = device_price * (severity / 60.0)
                price_increase = min(price_increase, device_price * 0.35)
                
                devices.append({
                    "device": r["device"],
                    "brand": r.get("brand", ""),
                    "current_price_usd": device_price,
                    "impact_score": round(severity / 10, 2),
                    "price_increase_usd": round(price_increase, 2),
                    "price_increase_pct": round(price_increase / device_price * 100, 1) if device_price else 0,
                    "recovery_months": _estimate_recovery(severity, "Country"),
                    "affected_components": r.get("affected_components", []),
                    "single_source_risk": False,
                    "units_sold_millions": r.get("units_sold", 0) or 0,
                })
        except Exception:
            pass
    
    devices.sort(key=lambda x: x["price_increase_usd"], reverse=True)
    return devices


def _shock_generic(
    conn, node_name: str, severity: int
) -> List[Dict[str, Any]]:
    """Generic shock simulation using path traversal."""
    escaped = node_name.replace("'", "\\'")
    query = f"""
    MATCH path = (start {{name: '{escaped}'}})-[*1..6]->(d:Device)
    WITH d,
         min(length(path)) AS min_hops,
         count(path) AS dependency_paths
    RETURN
        d.name AS device,
        d.brand AS brand,
        d.base_price_usd AS device_price,
        d.units_sold_millions AS units_sold,
        min_hops,
        dependency_paths
    ORDER BY min_hops ASC
    """
    
    try:
        results = conn.execute_and_fetch(query)
        devices = []
        
        for r in results:
            device_price = r.get("device_price", 0) or 0
            hops = r.get("min_hops", 3) or 3
            price_increase = device_price * (severity / 100.0) * (6.0 / hops)
            price_increase = min(price_increase, device_price * 0.3)
            
            devices.append({
                "device": r["device"],
                "brand": r.get("brand", ""),
                "current_price_usd": device_price,
                "impact_score": round(severity / hops, 2),
                "price_increase_usd": round(price_increase, 2),
                "price_increase_pct": round(price_increase / device_price * 100, 1) if device_price else 0,
                "recovery_months": _estimate_recovery(severity, "Material"),
                "affected_components": [],
                "single_source_risk": False,
                "units_sold_millions": r.get("units_sold", 0) or 0,
            })
        
        return devices
    except Exception:
        return []


def _build_ripple_path(conn, node_name: str, node_type: str) -> List[str]:
    """Build a human-readable ripple path from the disrupted node."""
    escaped = node_name.replace("'", "\\'")
    
    try:
        query = f"""
        MATCH path = (start {{name: '{escaped}'}})-[*1..4]->(end)
        WITH [node IN nodes(path) | node.name] AS chain
        RETURN chain
        LIMIT 5
        """
        results = conn.execute_and_fetch(query)
        
        paths = []
        for r in results:
            paths.append(" → ".join(r["chain"]))
        
        return paths if paths else [f"{node_name} → (calculating impact...)"]
    except Exception:
        return [f"{node_name} → (calculating impact...)"]


def _estimate_recovery(severity: int, node_type: str) -> int:
    """Estimate recovery time in months based on severity and type."""
    base_months = {
        "Material": 6,
        "Company": 12,
        "Country": 18,
    }
    base = base_months.get(node_type, 12)
    return max(1, int(base * severity / 10))


def calculate_overall_risk_score() -> float:
    """
    Calculate an overall supply chain fragility score (0-10).
    
    Factors:
    - Concentration of critical minerals in single countries
    - Single-source component dependencies
    - Geopolitical risk of key countries
    """
    conn = get_connection()
    
    score = 0.0
    factors = 0
    
    # Factor 1: Material concentration
    try:
        results = conn.execute_and_fetch(
            "MATCH (m:Material) WHERE m.criticality_score >= 8 "
            "RETURN avg(m.criticality_score) AS avg_criticality"
        )
        if results:
            score += results[0].get("avg_criticality", 5)
            factors += 1
    except Exception:
        pass
    
    # Factor 2: Single-source components
    try:
        results = conn.execute_and_fetch(
            "MATCH (c:Component) "
            "RETURN "
            "  toFloat(sum(CASE WHEN c.single_sourced = true THEN 1 ELSE 0 END)) / "
            "  toFloat(count(c)) * 10 AS single_source_ratio"
        )
        if results:
            score += results[0].get("single_source_ratio", 5)
            factors += 1
    except Exception:
        pass
    
    # Factor 3: Country risk
    try:
        results = conn.execute_and_fetch(
            "MATCH (c:Country) WHERE c.geopolitical_risk_score >= 7 "
            "RETURN count(c) AS high_risk_countries"
        )
        if results:
            high_risk = results[0].get("high_risk_countries", 3)
            score += min(high_risk, 10)
            factors += 1
    except Exception:
        pass
    
    overall = score / max(factors, 1)
    return round(overall, 1)


def main() -> None:
    """Run supply chain shock simulation demo."""
    logger.info("═" * 55)
    logger.info("⚡ PhoneGraph: Supply Chain Shock Simulator")
    logger.info("═" * 55)
    
    # Scenario 1: Gallium export ban
    print("\n📌 Scenario 1: China bans Gallium exports (severity: 8/10)")
    print("─" * 50)
    result = simulate_supply_shock("Gallium", "Material", 8)
    _print_shock_results(result)
    
    # Scenario 2: TSMC disruption
    print("\n📌 Scenario 2: TSMC production halt (severity: 10/10)")
    print("─" * 50)
    result = simulate_supply_shock("TSMC", "Company", 10)
    _print_shock_results(result)
    
    # Scenario 3: Taiwan blockade
    print("\n📌 Scenario 3: Taiwan blockade (severity: 9/10)")
    print("─" * 50)
    result = simulate_supply_shock("Taiwan", "Country", 9)
    _print_shock_results(result)
    
    # Overall risk score
    risk = calculate_overall_risk_score()
    print(f"\n🌡️ Overall Supply Chain Fragility Score: {risk}/10")
    
    logger.info("✅ Shock simulation complete")


def _print_shock_results(result: Dict[str, Any]) -> None:
    """Pretty print shock simulation results."""
    devices = result.get("affected_devices", [])
    
    if not devices:
        print("   No devices directly affected (check graph connectivity)")
        return
    
    print(f"\n   Affected devices: {len(devices)}")
    print(f"   Most vulnerable: {result.get('most_vulnerable', 'N/A')}")
    print(f"   Recovery estimate: {result.get('recovery_estimate_months', 0)} months")
    print(f"\n   {'Device':<30} {'Price Impact':<15} {'% Change':<10}")
    print("   " + "─" * 55)
    
    for d in devices[:8]:
        print(f"   {d['device']:<30} "
              f"+${d['price_increase_usd']:<13.2f} "
              f"+{d['price_increase_pct']}%")
    
    if result.get("ripple_path"):
        print(f"\n   Ripple paths:")
        for path in result["ripple_path"][:3]:
            print(f"   • {path}")


if __name__ == "__main__":
    main()
