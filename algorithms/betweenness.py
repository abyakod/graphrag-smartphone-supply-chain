"""
PhoneGraph: Betweenness Centrality Algorithm Runner

Identifies hidden chokepoints in the supply chain — nodes that
sit between the most shortest paths. Remove a high-betweenness
node and the entire chain breaks.

Run standalone: python -m algorithms.betweenness
"""

import logging
import sys

from graph.algorithms import run_betweenness_centrality

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run Betweenness Centrality and display results."""
    logger.info("═" * 55)
    logger.info("🔗 PhoneGraph: Betweenness Centrality — Hidden Chokepoints")
    logger.info("═" * 55)
    
    results = run_betweenness_centrality(limit=10)
    
    if not results:
        logger.error("No results — is the graph populated?")
        sys.exit(1)
    
    print("\n🎯 Top 10 Hidden Chokepoints:")
    print("─" * 55)
    print(f"{'Rank':<5} {'Name':<30} {'Type':<12} {'Centrality':<12}")
    print("─" * 55)
    
    for i, r in enumerate(results, 1):
        print(f"{i:<5} {r['name']:<30} {r['type']:<12} "
              f"{r['betweenness_centrality']:.6f}")
    
    print("─" * 55)
    
    if results:
        top = results[0]
        print(f"\n💡 Key Insight: {top['name']} ({top['type']}) is the "
              f"BIGGEST CHOKEPOINT in the supply chain.")
        print(f"   Remove this node and {top['type'].lower()} supply chains break.")
    
    logger.info("✅ Betweenness Centrality analysis complete")


if __name__ == "__main__":
    main()
