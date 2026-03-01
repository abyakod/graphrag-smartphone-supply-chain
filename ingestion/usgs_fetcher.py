"""
PhoneGraph: USGS Critical Minerals Data Fetcher

Provides real USGS critical minerals data for the 7 minerals
critical to smartphone manufacturing. Uses local JSON data
with hardcoded fallback based on verified public data.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════
# Hardcoded Real Data — USGS Critical Minerals
# Source: https://minerals.usgs.gov/minerals/pubs/commodity/
# ═══════════════════════════════════════════════════

MINERALS_DATA: Dict[str, Dict[str, Any]] = {
    "Gallium": {
        "type": "metal",
        "annual_production_tons": 300,
        "primary_country": "China",
        "china_share_pct": 80,
        "export_restricted": True,
        "restriction_date": "2023-07-01",
        "price_usd_per_kg": 222,
        "criticality_score": 9,
        "used_in": ["GaN Chips", "GaAs Chips", "LEDs", "Solar Panels", "5G RF Modules"],
        "extraction_countries": {
            "China": 80, "Japan": 8, "South Korea": 5,
            "Russia": 4, "Germany": 3,
        },
    },
    "Neon": {
        "type": "noble_gas",
        "annual_production_tons": 540,
        "primary_country": "Ukraine",
        "ukraine_russia_share_pct": 90,
        "export_restricted": False,
        "price_usd_per_kg": 850,
        "criticality_score": 10,
        "used_in": ["EUV Lithography Systems", "DUV Lithography Systems", "Excimer Lasers"],
        "extraction_countries": {
            "Ukraine": 45, "Russia": 45, "China": 5,
            "USA": 3, "Japan": 2,
        },
    },
    "Cobalt": {
        "type": "metal",
        "annual_production_tons": 190000,
        "primary_country": "DRC",
        "drc_share_pct": 70,
        "export_restricted": False,
        "price_usd_per_kg": 33,
        "criticality_score": 8,
        "used_in": ["Li-Ion Battery Cathodes", "Superalloys", "Magnetic Materials"],
        "extraction_countries": {
            "DRC": 70, "Russia": 5, "Australia": 4,
            "Philippines": 4, "Canada": 3,
        },
    },
    "Rare Earth Elements": {
        "type": "mineral_group",
        "annual_production_tons": 300000,
        "primary_country": "China",
        "china_share_pct": 60,
        "export_restricted": False,
        "price_usd_per_kg": 45,
        "criticality_score": 9,
        "used_in": ["Speakers", "Haptic Motors", "Permanent Magnets", "Camera Lenses"],
        "extraction_countries": {
            "China": 60, "USA": 14, "Myanmar": 10,
            "Australia": 8, "India": 5,
        },
    },
    "Lithium": {
        "type": "metal",
        "annual_production_tons": 130000,
        "primary_country": "Australia",
        "top_producers_share_pct": 90,
        "export_restricted": False,
        "price_usd_per_kg": 14,
        "criticality_score": 8,
        "used_in": ["Li-Ion Batteries", "Ceramic Glass", "Lubricants"],
        "extraction_countries": {
            "Australia": 47, "Chile": 24, "China": 15,
            "Argentina": 6, "Brazil": 3,
        },
    },
    "Indium": {
        "type": "metal",
        "annual_production_tons": 900,
        "primary_country": "China",
        "china_share_pct": 70,
        "export_restricted": False,
        "price_usd_per_kg": 250,
        "criticality_score": 7,
        "used_in": ["ITO Touchscreens", "OLED Displays", "Thin-Film Solar Cells"],
        "extraction_countries": {
            "China": 70, "South Korea": 10, "Japan": 8,
            "Canada": 5, "France": 3,
        },
    },
    "Germanium": {
        "type": "metalloid",
        "annual_production_tons": 130,
        "primary_country": "China",
        "china_share_pct": 60,
        "export_restricted": True,
        "restriction_date": "2023-08-01",
        "price_usd_per_kg": 1500,
        "criticality_score": 8,
        "used_in": [
            "Fiber Optic Cables", "Infrared Optics",
            "Solar Cells", "Camera Lenses",
        ],
        "extraction_countries": {
            "China": 60, "Belgium": 15, "Russia": 10,
            "USA": 8, "Canada": 5,
        },
    },
}


def fetch_minerals() -> Dict[str, Dict[str, Any]]:
    """
    Fetch critical minerals data.
    
    Attempts to load from local JSON file first, falls back
    to hardcoded data if file is unavailable.
    
    Returns:
        Dictionary mapping mineral name to its data
    """
    data_path = Path(__file__).parent.parent / "data" / "raw" / "usgs_critical_minerals.json"
    
    if data_path.exists():
        try:
            with open(data_path, "r") as f:
                raw = json.load(f)
            minerals = {m["name"]: m for m in raw.get("minerals", [])}
            logger.info(f"📦 Loaded {len(minerals)} minerals from {data_path}")
            return minerals
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"⚠️ Error reading JSON file: {e}, using fallback data")
    
    logger.info(f"📦 Using hardcoded USGS minerals data ({len(MINERALS_DATA)} minerals)")
    return MINERALS_DATA


def get_all_components_from_minerals() -> List[str]:
    """
    Extract all unique component names from minerals' used_in fields.
    
    Returns:
        Sorted list of component names
    """
    components = set()
    for mineral_data in MINERALS_DATA.values():
        components.update(mineral_data.get("used_in", []))
    return sorted(components)


def get_all_countries_from_minerals() -> List[str]:
    """
    Extract all unique country names from minerals' extraction data.
    
    Returns:
        Sorted list of country names
    """
    countries = set()
    for mineral_data in MINERALS_DATA.values():
        countries.update(mineral_data.get("extraction_countries", {}).keys())
    return sorted(countries)
