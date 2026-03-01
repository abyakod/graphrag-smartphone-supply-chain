"""
PhoneGraph: PageRank Algorithm Runner

Runs PageRank on the supply chain graph to identify the most
influential/critical nodes. Higher PageRank = more dependent
nodes downstream.

Run standalone: python -m algorithms.pagerank
"""

import logging
import sys

from graph.connection import get_connection
from graph.algorithms import run_pagerank

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run PageRank and display results."""
    logger.info("═" * 55)
    logger.info("📊 PhoneGraph: PageRank — Most Critical Nodes")
    logger.info("═" * 55)
    
    results = run_pagerank(limit=20)
    
    if not results:
        logger.error("No PageRank results — is the graph populated?")
        sys.exit(1)
    
    # Display results
    print("\n🏆 Top 20 Nodes by PageRank:")
    print("─" * 50)
    print(f"{'Rank':<5} {'Name':<30} {'Type':<12} {'Score':<10}")
    print("─" * 50)
    
    for i, r in enumerate(results, 1):
        print(f"{i:<5} {r['name']:<30} {r['type']:<12} {r['rank']:.6f}")
    
    print("─" * 50)
    
    # Highlight key insight
    if results:
        top = results[0]
        print(f"\n💡 Key Insight: {top['name']} ({top['type']}) is the "
              f"MOST CRITICAL node in the entire supply chain.")
        print(f"   PageRank score: {top['rank']:.6f}")
        
        if top['name'] in ('ASML', 'TSMC'):
            print(f"   This confirms: {top['name']} is THE single biggest "
                  f"chokepoint in global smartphone production.")
    
    logger.info("✅ PageRank analysis complete")


if __name__ == "__main__":
    main()
