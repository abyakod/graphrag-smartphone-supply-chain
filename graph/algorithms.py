"""
PhoneGraph: Graph Algorithm Wrappers

Wraps Memgraph MAGE library algorithms with error handling,
logging, and result formatting. All algorithms use the MAGE
procedures pre-installed in the memgraph-mage Docker image.
"""

import logging
from typing import Any, Dict, List, Optional

from graph.connection import get_connection
from graph import queries

logger = logging.getLogger(__name__)


def run_pagerank(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Run PageRank algorithm on the entire graph.
    
    Identifies the most influential nodes — those that many other
    nodes depend on. Higher PageRank = bigger chokepoint in the
    supply chain.
    
    Args:
        limit: Maximum number of results to return
        
    Returns:
        List of dicts with keys: name, type, rank
    """
    conn = get_connection()
    logger.info("📊 Running PageRank algorithm...")
    
    try:
        query = f"""
        CALL pagerank.get()
        YIELD node, rank
        RETURN node.name AS name, labels(node)[0] AS type, rank
        ORDER BY rank DESC
        LIMIT {limit}
        """
        results = conn.execute_and_fetch(query)
        
        formatted = [
            {"name": r["name"], "type": r["type"], "rank": round(r["rank"], 6)}
            for r in results
        ]
        
        logger.info(f"✅ PageRank completed: Top node = {formatted[0]['name']} "
                    f"(rank: {formatted[0]['rank']})" if formatted else "No results")
        return formatted
        
    except Exception as e:
        logger.error(f"❌ PageRank failed: {e}")
        logger.info("Falling back to degree-based ranking...")
        return _fallback_pagerank(conn, limit)


def _fallback_pagerank(conn, limit: int) -> List[Dict[str, Any]]:
    """Fallback ranking using node degree when MAGE is unavailable."""
    query = f"""
    MATCH (n)
    OPTIONAL MATCH (n)-[r]-()
    WITH n, count(r) AS degree
    RETURN n.name AS name, labels(n)[0] AS type, 
           toFloat(degree) / 100.0 AS rank
    ORDER BY degree DESC
    LIMIT {limit}
    """
    results = conn.execute_and_fetch(query)
    return [
        {"name": r["name"], "type": r["type"], "rank": round(r["rank"], 6)}
        for r in results
    ]


def run_betweenness_centrality(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Run Betweenness Centrality algorithm.
    
    Finds nodes that sit between the most shortest paths.
    High betweenness = remove this node and the supply chain
    breaks. Critical for identifying hidden chokepoints.
    
    Args:
        limit: Maximum number of results to return
        
    Returns:
        List of dicts with keys: name, type, betweenness_centrality
    """
    conn = get_connection()
    logger.info("🔗 Running Betweenness Centrality algorithm...")
    
    try:
        query = f"""
        CALL betweenness_centrality.get(FALSE, FALSE)
        YIELD node, betweenness_centrality
        RETURN node.name AS name, labels(node)[0] AS type, betweenness_centrality
        ORDER BY betweenness_centrality DESC
        LIMIT {limit}
        """
        results = conn.execute_and_fetch(query)
        
        formatted = [
            {
                "name": r["name"],
                "type": r["type"],
                "betweenness_centrality": round(r["betweenness_centrality"], 6),
            }
            for r in results
        ]
        
        logger.info(f"✅ Betweenness Centrality completed: Top chokepoint = "
                    f"{formatted[0]['name']}" if formatted else "No results")
        return formatted
        
    except Exception as e:
        logger.error(f"❌ Betweenness Centrality failed: {e}")
        logger.info("Falling back to degree-based centrality...")
        return _fallback_betweenness(conn, limit)


def _fallback_betweenness(conn, limit: int) -> List[Dict[str, Any]]:
    """Fallback centrality using in/out degree ratio when MAGE unavailable."""
    query = f"""
    MATCH (n)
    OPTIONAL MATCH (n)-[r_out]->()
    OPTIONAL MATCH ()-[r_in]->(n)
    WITH n, count(DISTINCT r_out) AS out_deg, count(DISTINCT r_in) AS in_deg
    RETURN n.name AS name, labels(n)[0] AS type,
           toFloat(out_deg * in_deg) / 10.0 AS betweenness_centrality
    ORDER BY betweenness_centrality DESC
    LIMIT {limit}
    """
    results = conn.execute_and_fetch(query)
    return [
        {
            "name": r["name"],
            "type": r["type"],
            "betweenness_centrality": round(r["betweenness_centrality"], 6),
        }
        for r in results
    ]


def run_community_detection() -> List[Dict[str, Any]]:
    """
    Run Community Detection (Louvain/LabelRank) algorithm.
    
    Discovers natural clusters/ecosystems in the supply chain.
    Expected result: Apple ecosystem, Samsung ecosystem, 
    China raw materials cluster.
    
    Returns:
        List of dicts with keys: community_id, members, size
    """
    conn = get_connection()
    logger.info("🏘️ Running Community Detection algorithm...")
    
    try:
        results = conn.execute_and_fetch(queries.COMMUNITY_DETECTION_QUERY)
        
        formatted = [
            {
                "community_id": r["community_id"],
                "members": r["members"],
                "size": r["size"],
            }
            for r in results
        ]
        
        logger.info(f"✅ Community Detection completed: "
                    f"Found {len(formatted)} communities")
        return formatted
        
    except Exception as e:
        logger.error(f"❌ Community Detection failed: {e}")
        logger.info("Falling back to label-based clustering...")
        return _fallback_communities(conn)


def _fallback_communities(conn) -> List[Dict[str, Any]]:
    """Fallback clustering by node label when MAGE unavailable."""
    query = """
    MATCH (n)
    WITH labels(n)[0] AS label, collect(n.name) AS members
    RETURN label AS community_id, members, size(members) AS size
    ORDER BY size DESC
    """
    results = conn.execute_and_fetch(query)
    return [
        {
            "community_id": r["community_id"],
            "members": r["members"],
            "size": r["size"],
        }
        for r in results
    ]


def find_shortest_path(
    start_node: str, end_node: str
) -> Optional[Dict[str, Any]]:
    """
    Find the shortest path between two nodes in the graph.
    
    Essential for answering "How does Material X reach Device Y?"
    questions. Shows the minimum number of hops from raw material
    to finished device.
    
    Args:
        start_node: Name of the starting node (e.g., "Gallium")
        end_node: Name of the ending node (e.g., "iPhone 16 Pro")
        
    Returns:
        Dict with keys: supply_chain, node_types, hops
        or None if no path exists
    """
    conn = get_connection()
    logger.info(f"🗺️ Finding shortest path: {start_node} → {end_node}")
    
    try:
        query = """
        MATCH path = shortestPath(
          (start {name: $start_node})-[*]-(end {name: $end_node})
        )
        RETURN
          [node IN nodes(path) | node.name] AS supply_chain,
          [node IN nodes(path) | labels(node)[0]] AS node_types,
          [r IN relationships(path) | type(r)] AS relationship_types,
          length(path) AS hops
        """
        results = conn.execute_and_fetch(query)
        
        if results:
            r = results[0]
            result = {
                "supply_chain": r["supply_chain"],
                "node_types": r["node_types"],
                "relationship_types": r["relationship_types"],
                "hops": r["hops"],
            }
            logger.info(f"✅ Path found: {' → '.join(r['supply_chain'])} "
                       f"({r['hops']} hops)")
            return result
        else:
            logger.warning(f"⚠️ No path found between {start_node} and {end_node}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Shortest path query failed: {e}")
        return None


def get_subgraph(node_name: str, hops: int = 2) -> Dict[str, List]:
    """
    Extract a subgraph centered on a specific node.
    
    Used for visualization — returns nodes and edges within
    N hops of the center node.
    
    Args:
        node_name: Center node name
        hops: Number of hops to traverse (default: 2)
        
    Returns:
        Dict with keys: nodes, edges
    """
    conn = get_connection()
    escaped = node_name.replace("'", "\\'")
    logger.info(f"🕸️ Extracting subgraph around '{node_name}' ({hops} hops)")
    
    # Simple pattern-based traversal (works with all Memgraph versions)
    try:
        node_query = f"""
        MATCH path = (start {{name: '{escaped}'}})-[*1..{hops}]-(connected)
        WITH start, collect(DISTINCT connected) AS neighbors
        WITH neighbors + [start] AS all_nodes
        UNWIND all_nodes AS n
        RETURN DISTINCT id(n) AS id, n.name AS name, labels(n)[0] AS type,
               properties(n) AS properties
        """
        edge_query = f"""
        MATCH path = (start {{name: '{escaped}'}})-[*1..{hops}]-(connected)
        WITH start, collect(DISTINCT connected) AS neighbors
        WITH neighbors + [start] AS all_nodes
        UNWIND all_nodes AS a
        MATCH (a)-[r]->(b)
        WHERE b IN all_nodes
        RETURN DISTINCT a.name AS source, b.name AS target, 
               type(r) AS type, properties(r) AS properties
        """
        nodes = conn.execute_and_fetch(node_query)
        edges = conn.execute_and_fetch(edge_query)
        
        return {
            "nodes": [dict(n) for n in nodes],
            "edges": [dict(e) for e in edges],
        }
    except Exception as e:
        logger.error(f"❌ Subgraph extraction failed: {e}")
        return {"nodes": [], "edges": []}
