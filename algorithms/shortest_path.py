"""
PhoneGraph: Shortest Path Algorithm Runner

Finds the minimum-hop path from raw material to finished device.
Answers "How does Gallium reach iPhone 16?" type questions.

Run standalone: python -m algorithms.shortest_path
"""

import logging
import sys
from typing import Optional

from graph.algorithms import find_shortest_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════
# Interesting paths to trace
# ═══════════════════════════════════════════════════

EXAMPLE_PATHS = [
    ("Gallium", "iPhone 16 Pro", "From Chinese mine to your pocket"),
    ("Neon", "Samsung Galaxy S25 Ultra", "Ukrainian gas to Korean flagship"),
    ("Cobalt", "iPhone 16 Pro", "Congo cobalt to Apple battery"),
    ("Lithium", "Google Pixel 9 Pro", "Australian lithium to Google phone"),
    ("Rare Earth Elements", "Xiaomi 15 Ultra", "Chinese minerals to Xiaomi"),
]


def trace_path(start: str, end: str, description: str = "") -> Optional[dict]:
    """
    Trace and display a supply chain path.
    
    Args:
        start: Starting node name
        end: Ending node name
        description: Human-readable description
        
    Returns:
        Path result dict or None
    """
    if description:
        print(f"\n🗺️ {description}")
    
    result = find_shortest_path(start, end)
    
    if result:
        chain = result["supply_chain"]
        types = result["node_types"]
        hops = result["hops"]
        
        print(f"   Path ({hops} hops):")
        for i, (node, node_type) in enumerate(zip(chain, types)):
            connector = "   └─→ " if i == len(chain) - 1 else "   ├─→ "
            print(f"{connector}[{node_type}] {node}")
        
        if result.get("relationship_types"):
            rels = " → ".join(result["relationship_types"])
            print(f"   Relationships: {rels}")
    else:
        print(f"   ❌ No path found between {start} and {end}")
    
    return result


def main() -> None:
    """Run all example shortest paths."""
    logger.info("═" * 55)
    logger.info("🗺️ PhoneGraph: Shortest Paths — Mine to Pocket")
    logger.info("═" * 55)
    
    print("\n📍 Tracing supply chain paths from raw materials to devices:")
    print("─" * 55)
    
    for start, end, desc in EXAMPLE_PATHS:
        trace_path(start, end, desc)
    
    print("\n" + "─" * 55)
    print("\n💡 Key Insight: Even the shortest supply chain path from")
    print("   raw material to your phone involves 4-6 hops across")
    print("   multiple countries, companies, and components.")
    
    logger.info("✅ Shortest Path analysis complete")


if __name__ == "__main__":
    main()
