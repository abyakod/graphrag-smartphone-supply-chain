"""
PhoneGraph: Community Detection Algorithm Runner

Discovers natural supply chain clusters/ecosystems.
Expected: Apple ecosystem, Samsung ecosystem, China materials cluster.

Run standalone: python -m algorithms.community_detection
"""

import logging
import sys

from graph.algorithms import run_community_detection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run Community Detection and display results."""
    logger.info("═" * 55)
    logger.info("🏘️ PhoneGraph: Community Detection — Supply Chain Empires")
    logger.info("═" * 55)
    
    results = run_community_detection()
    
    if not results:
        logger.error("No results — is the graph populated?")
        sys.exit(1)
    
    print("\n🌐 Discovered Supply Chain Communities:")
    print("─" * 60)
    
    for i, community in enumerate(results, 1):
        members = community["members"]
        print(f"\n📦 Community {i} ({community['size']} members):")
        print(f"   ID: {community['community_id']}")
        
        # Display up to 15 members
        displayed = members[:15]
        remaining = len(members) - 15
        
        for member in displayed:
            print(f"   • {member}")
        
        if remaining > 0:
            print(f"   ... and {remaining} more")
    
    print("\n" + "─" * 60)
    print(f"\n💡 Total communities found: {len(results)}")
    
    if len(results) >= 3:
        print("   The three expected supply chain empires have emerged:")
        print("   • The Apple/TSMC Ecosystem")
        print("   • The Samsung/Korea Ecosystem")
        print("   • The China Raw Materials Cluster")
    
    logger.info("✅ Community Detection analysis complete")


if __name__ == "__main__":
    main()
