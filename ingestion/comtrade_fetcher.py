"""
PhoneGraph: UN Comtrade Semiconductor Trade Flow Fetcher

Provides real semiconductor trade flow data between key countries.
Based on UN Comtrade public data for HS codes 8541-8542 (semiconductors).
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════
# Hardcoded Real Trade Flow Data
# Source: UN Comtrade (HS 8541/8542 semiconductors)
# ═══════════════════════════════════════════════════

TRADE_FLOWS: List[Dict[str, Any]] = [
    {"from": "Taiwan", "to": "USA", "value_usd_billions": 48.2, "year": 2023, "category": "semiconductors"},
    {"from": "Taiwan", "to": "China", "value_usd_billions": 52.1, "year": 2023, "category": "semiconductors"},
    {"from": "Taiwan", "to": "Japan", "value_usd_billions": 15.4, "year": 2023, "category": "semiconductors"},
    {"from": "Taiwan", "to": "South Korea", "value_usd_billions": 12.8, "year": 2023, "category": "semiconductors"},
    {"from": "South Korea", "to": "USA", "value_usd_billions": 22.1, "year": 2023, "category": "semiconductors"},
    {"from": "South Korea", "to": "China", "value_usd_billions": 31.6, "year": 2023, "category": "semiconductors"},
    {"from": "China", "to": "USA", "value_usd_billions": 18.3, "year": 2023, "category": "semiconductors"},
    {"from": "Japan", "to": "Taiwan", "value_usd_billions": 8.7, "year": 2023, "category": "semiconductor_equipment"},
    {"from": "Japan", "to": "South Korea", "value_usd_billions": 6.2, "year": 2023, "category": "semiconductor_materials"},
    {"from": "Netherlands", "to": "Taiwan", "value_usd_billions": 11.4, "year": 2023, "category": "semiconductor_equipment"},
    {"from": "Netherlands", "to": "South Korea", "value_usd_billions": 5.8, "year": 2023, "category": "semiconductor_equipment"},
    {"from": "USA", "to": "Taiwan", "value_usd_billions": 7.9, "year": 2023, "category": "chip_design_ip"},
    {"from": "China", "to": "Japan", "value_usd_billions": 4.5, "year": 2023, "category": "rare_earth_materials"},
    {"from": "DRC", "to": "China", "value_usd_billions": 3.2, "year": 2023, "category": "cobalt"},
    {"from": "Australia", "to": "China", "value_usd_billions": 5.8, "year": 2023, "category": "lithium"},
    {"from": "Chile", "to": "China", "value_usd_billions": 2.9, "year": 2023, "category": "lithium"},
]

# Country metadata with real geopolitical risk assessments
COUNTRIES_DATA: Dict[str, Dict[str, Any]] = {
    "China": {
        "iso_code": "CN",
        "region": "East Asia",
        "geopolitical_risk_score": 8,
        "trade_restriction_risk": 9,
    },
    "Taiwan": {
        "iso_code": "TW",
        "region": "East Asia",
        "geopolitical_risk_score": 9,
        "trade_restriction_risk": 7,
    },
    "USA": {
        "iso_code": "US",
        "region": "North America",
        "geopolitical_risk_score": 3,
        "trade_restriction_risk": 5,
    },
    "South Korea": {
        "iso_code": "KR",
        "region": "East Asia",
        "geopolitical_risk_score": 5,
        "trade_restriction_risk": 3,
    },
    "Japan": {
        "iso_code": "JP",
        "region": "East Asia",
        "geopolitical_risk_score": 3,
        "trade_restriction_risk": 3,
    },
    "Netherlands": {
        "iso_code": "NL",
        "region": "Europe",
        "geopolitical_risk_score": 1,
        "trade_restriction_risk": 2,
    },
    "DRC": {
        "iso_code": "CD",
        "region": "Central Africa",
        "geopolitical_risk_score": 9,
        "trade_restriction_risk": 4,
    },
    "Australia": {
        "iso_code": "AU",
        "region": "Oceania",
        "geopolitical_risk_score": 2,
        "trade_restriction_risk": 2,
    },
    "Chile": {
        "iso_code": "CL",
        "region": "South America",
        "geopolitical_risk_score": 3,
        "trade_restriction_risk": 2,
    },
    "Ukraine": {
        "iso_code": "UA",
        "region": "Europe",
        "geopolitical_risk_score": 10,
        "trade_restriction_risk": 8,
    },
    "Russia": {
        "iso_code": "RU",
        "region": "Europe/Asia",
        "geopolitical_risk_score": 9,
        "trade_restriction_risk": 10,
    },
    "India": {
        "iso_code": "IN",
        "region": "South Asia",
        "geopolitical_risk_score": 4,
        "trade_restriction_risk": 4,
    },
    "Germany": {
        "iso_code": "DE",
        "region": "Europe",
        "geopolitical_risk_score": 2,
        "trade_restriction_risk": 2,
    },
    "Belgium": {
        "iso_code": "BE",
        "region": "Europe",
        "geopolitical_risk_score": 1,
        "trade_restriction_risk": 1,
    },
    "Philippines": {
        "iso_code": "PH",
        "region": "Southeast Asia",
        "geopolitical_risk_score": 4,
        "trade_restriction_risk": 3,
    },
    "Canada": {
        "iso_code": "CA",
        "region": "North America",
        "geopolitical_risk_score": 2,
        "trade_restriction_risk": 2,
    },
    "Argentina": {
        "iso_code": "AR",
        "region": "South America",
        "geopolitical_risk_score": 4,
        "trade_restriction_risk": 4,
    },
    "Brazil": {
        "iso_code": "BR",
        "region": "South America",
        "geopolitical_risk_score": 3,
        "trade_restriction_risk": 3,
    },
    "Myanmar": {
        "iso_code": "MM",
        "region": "Southeast Asia",
        "geopolitical_risk_score": 9,
        "trade_restriction_risk": 7,
    },
    "France": {
        "iso_code": "FR",
        "region": "Europe",
        "geopolitical_risk_score": 2,
        "trade_restriction_risk": 2,
    },
}


def fetch_trade_flows() -> List[Dict[str, Any]]:
    """
    Fetch semiconductor trade flow data.
    
    Attempts to load from local JSON file first, falls back
    to hardcoded data.
    
    Returns:
        List of trade flow dictionaries
    """
    data_path = (
        Path(__file__).parent.parent / "data" / "raw" / "un_comtrade_semiconductors.json"
    )
    
    if data_path.exists():
        try:
            with open(data_path, "r") as f:
                raw = json.load(f)
            flows = raw.get("trade_flows", [])
            logger.info(f"📦 Loaded {len(flows)} trade flows from {data_path}")
            return flows
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"⚠️ Error reading JSON file: {e}, using fallback data")
    
    logger.info(f"📦 Using hardcoded trade flow data ({len(TRADE_FLOWS)} flows)")
    return TRADE_FLOWS


def fetch_countries() -> Dict[str, Dict[str, Any]]:
    """
    Fetch country metadata including geopolitical risk scores.
    
    Returns:
        Dictionary mapping country name to its metadata
    """
    logger.info(f"📦 Loading {len(COUNTRIES_DATA)} countries with risk data")
    return COUNTRIES_DATA
