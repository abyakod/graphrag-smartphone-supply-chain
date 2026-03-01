"""
PhoneGraph: Graph Schema Definition

Defines all 7 node types and 10 relationship types for the
smartphone supply chain knowledge graph. Provides functions
to create indexes, constraints, and validate the schema.
"""

import logging
from typing import List

from graph.connection import get_connection

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════
# Node Type Definitions
# ═══════════════════════════════════════════════════

NODE_TYPES = {
    "Material": {
        "properties": [
            "name", "type", "annual_production_tons", "criticality_score",
            "primary_country", "export_restricted", "price_usd_per_kg"
        ],
        "description": "Raw materials used in semiconductor / device manufacturing",
    },
    "Company": {
        "properties": [
            "name", "country", "revenue_usd_billions", "market_cap_usd_billions",
            "type", "employees", "founded_year", "ticker_symbol"
        ],
        "description": "Manufacturers, foundries, OEMs, and suppliers",
    },
    "Component": {
        "properties": [
            "name", "category", "process_node_nm", "estimated_cost_usd",
            "lead_time_weeks", "single_sourced"
        ],
        "description": "Discrete components used in device assembly",
    },
    "Device": {
        "properties": [
            "name", "brand", "launch_year", "base_price_usd",
            "units_sold_millions", "market_segment"
        ],
        "description": "Consumer smartphones and end-user devices",
    },
    "Country": {
        "properties": [
            "name", "iso_code", "region", "geopolitical_risk_score",
            "trade_restriction_risk"
        ],
        "description": "Countries involved in the supply chain",
    },
    "RiskEvent": {
        "properties": [
            "name", "type", "date", "impact_severity",
            "description", "source_url"
        ],
        "description": "Geopolitical events, trade restrictions, natural disasters",
    },
    "Regulation": {
        "properties": [
            "name", "jurisdiction", "effective_date",
            "affected_materials", "penalty_description"
        ],
        "description": "Trade regulations, export controls, sanctions",
    },
}

# ═══════════════════════════════════════════════════
# Relationship Type Definitions
# ═══════════════════════════════════════════════════

RELATIONSHIP_TYPES = {
    "REQUIRED_FOR": {
        "from": "Material",
        "to": "Component",
        "properties": ["percentage"],
        "description": "Material is a required input for manufacturing a component",
    },
    "EXTRACTED_IN": {
        "from": "Material",
        "to": "Country",
        "properties": ["percentage"],
        "description": "Material is extracted/mined/produced in a country",
    },
    "MANUFACTURES": {
        "from": "Company",
        "to": "Component",
        "properties": ["capacity_units_per_year"],
        "description": "Company manufactures a component",
    },
    "SUPPLIES_TO": {
        "from": "Company",
        "to": "Company",
        "properties": ["contract_value_usd_m"],
        "description": "Company supplies goods/services to another company",
    },
    "HEADQUARTERED_IN": {
        "from": "Company",
        "to": "Country",
        "properties": [],
        "description": "Company has its headquarters in a country",
    },
    "USED_IN": {
        "from": "Component",
        "to": "Device",
        "properties": ["units_per_device"],
        "description": "Component is physically used inside a device",
    },
    "EXPORTS_TO": {
        "from": "Country",
        "to": "Country",
        "properties": ["value_usd_billions", "year"],
        "description": "Trade flow of semiconductors between countries",
    },
    "DISRUPTS": {
        "from": "RiskEvent",
        "to": "Material",
        "properties": ["severity"],
        "description": "A risk event disrupts the supply of a material",
    },
    "AFFECTS": {
        "from": "RiskEvent",
        "to": "Company",
        "properties": [],
        "description": "A risk event affects a company's operations",
    },
    "RESTRICTS": {
        "from": "Regulation",
        "to": "Material",
        "properties": [],
        "description": "A regulation restricts the trade of a material",
    },
}

# ═══════════════════════════════════════════════════
# Schema Creation Queries
# ═══════════════════════════════════════════════════

INDEX_QUERIES: List[str] = [
    # Unique constraints on name fields
    "CREATE INDEX ON :Material(name);",
    "CREATE INDEX ON :Company(name);",
    "CREATE INDEX ON :Component(name);",
    "CREATE INDEX ON :Device(name);",
    "CREATE INDEX ON :Country(name);",
    "CREATE INDEX ON :Country(iso_code);",
    "CREATE INDEX ON :RiskEvent(name);",
    "CREATE INDEX ON :Regulation(name);",
    # Additional indexes for frequent lookups
    "CREATE INDEX ON :Material(criticality_score);",
    "CREATE INDEX ON :Material(export_restricted);",
    "CREATE INDEX ON :Company(type);",
    "CREATE INDEX ON :Company(country);",
    "CREATE INDEX ON :Component(category);",
    "CREATE INDEX ON :Component(single_sourced);",
    "CREATE INDEX ON :Device(brand);",
    "CREATE INDEX ON :Country(region);",
    "CREATE INDEX ON :RiskEvent(type);",
    "CREATE INDEX ON :RiskEvent(impact_severity);",
]


def create_schema() -> None:
    """
    Create all indexes and constraints in Memgraph.
    
    Idempotent — safe to call multiple times.
    """
    conn = get_connection()
    logger.info("📋 Creating graph schema (indexes and constraints)...")
    
    for query in INDEX_QUERIES:
        try:
            conn.execute(query)
            logger.debug(f"  ✓ {query}")
        except Exception as e:
            # Index might already exist — that's OK
            if "already exists" in str(e).lower():
                logger.debug(f"  ⏭️ Index already exists: {query}")
            else:
                logger.warning(f"  ⚠️ Index creation warning: {e}")
    
    logger.info("✅ Schema created successfully")


def drop_schema() -> None:
    """Drop all indexes from Memgraph."""
    conn = get_connection()
    logger.info("🗑️ Dropping all indexes...")
    
    try:
        indexes = conn.execute_and_fetch("SHOW INDEX INFO")
        for idx in indexes:
            label = idx.get("label", "")
            prop = idx.get("property", "")
            if label and prop:
                try:
                    conn.execute(f"DROP INDEX ON :{label}({prop});")
                    logger.debug(f"  ✓ Dropped index on :{label}({prop})")
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"Could not drop indexes: {e}")
    
    logger.info("✅ Indexes dropped")


def validate_schema() -> dict:
    """
    Validate the current graph against the expected schema.
    
    Returns:
        dict with validation results per node type
    """
    conn = get_connection()
    validation = {}
    
    for label, definition in NODE_TYPES.items():
        result = conn.execute_and_fetch(
            f"MATCH (n:{label}) RETURN count(n) AS count"
        )
        count = result[0]["count"] if result else 0
        validation[label] = {
            "count": count,
            "expected_properties": definition["properties"],
            "status": "populated" if count > 0 else "empty",
        }
    
    return validation


def get_schema_summary() -> str:
    """
    Get a human-readable schema summary for use in LLM prompts.
    
    Returns:
        Formatted string describing all node and relationship types
    """
    lines = ["=== PhoneGraph Schema ===", "", "NODE TYPES:"]
    for label, defn in NODE_TYPES.items():
        props = ", ".join(defn["properties"])
        lines.append(f"  (:{label}) — {defn['description']}")
        lines.append(f"    Properties: {props}")
    
    lines.append("")
    lines.append("RELATIONSHIP TYPES:")
    for rel_type, defn in RELATIONSHIP_TYPES.items():
        props = ", ".join(defn["properties"]) if defn["properties"] else "none"
        lines.append(
            f"  (:{defn['from']})-[:{rel_type}]->(:{defn['to']}) "
            f"— {defn['description']}"
        )
        lines.append(f"    Properties: {props}")
    
    return "\n".join(lines)
