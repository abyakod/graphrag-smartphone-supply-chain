"""
PhoneGraph: Hybrid Retriever (Vector + Graph)

Combines vector similarity search with graph traversal to
retrieve the most relevant context for answering supply chain
questions. The graph traversal is key — it follows relationships
to find multi-hop connections that pure text search misses.
"""

import logging
from typing import Any, Dict, List, Optional

from graph.connection import get_connection
from graph.algorithms import find_shortest_path, get_subgraph
from graphrag.embeddings import (
    build_embedding_index,
    find_similar_nodes,
    get_all_node_texts,
)

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid retriever combining vector similarity with graph traversal.
    
    Strategy:
    1. Vector search: Find relevant starting nodes
    2. Graph expansion: Traverse relationships from those nodes
    3. Context assembly: Combine both into a rich context string
    """
    
    def __init__(self) -> None:
        self.conn = get_connection()
        self._embedding_index: Optional[Dict[str, Any]] = None
        self._node_texts: Optional[List[Dict[str, str]]] = None
    
    def _ensure_index(self) -> None:
        """Build embedding index if not already built."""
        if self._embedding_index is None:
            self._embedding_index = build_embedding_index()
        if self._node_texts is None:
            self._node_texts = get_all_node_texts()
    
    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        graph_hops: int = 2,
    ) -> Dict[str, Any]:
        """
        Retrieve context for a question using hybrid vector+graph approach.
        
        Args:
            question: User's question
            top_k: Number of initial nodes from vector search
            graph_hops: Number of hops to traverse in graph expansion
            
        Returns:
            Dict with keys: context, nodes, paths, method
        """
        logger.info(f"🔍 Hybrid retrieval for: '{question}'")
        
        # Step 1: Try vector similarity search
        vector_results = self._vector_search(question, top_k)
        
        # Step 2: Graph expansion from found nodes
        graph_context = self._graph_expand(vector_results, graph_hops)
        
        # Step 3: Keyword-based graph search (always runs as fallback)
        keyword_context = self._keyword_graph_search(question)
        
        # Step 4: Combine all context
        combined_context = self._combine_context(
            vector_results, graph_context, keyword_context, graph_hops
        )
        
        return combined_context
    
    def _vector_search(
        self, question: str, top_k: int
    ) -> List[Dict[str, Any]]:
        """Find relevant nodes via vector similarity."""
        self._ensure_index()
        
        if self._embedding_index is not None:
            results = find_similar_nodes(question, self._embedding_index, top_k)
            logger.info(f"  📎 Vector search found {len(results)} nodes")
            return results
        
        # Fallback: keyword matching
        logger.info("  📎 Vector search unavailable, using keyword matching")
        return self._keyword_match_nodes(question)
    
    def _keyword_match_nodes(
        self, question: str
    ) -> List[Dict[str, Any]]:
        """Fallback keyword matching when embeddings aren't available."""
        if self._node_texts is None:
            self._node_texts = get_all_node_texts()
        
        question_lower = question.lower()
        results = []
        
        for node in self._node_texts:
            name_lower = node["name"].lower()
            text_lower = node["text"].lower()
            
            # Simple relevance scoring
            score = 0.0
            if name_lower in question_lower:
                score = 0.9
            elif any(word in question_lower for word in name_lower.split()):
                score = 0.6
            elif any(word in text_lower for word in question_lower.split() if len(word) > 3):
                score = 0.3
            
            if score > 0:
                results.append({
                    "name": node["name"],
                    "label": node["label"],
                    "text": node["text"],
                    "similarity": score,
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:5]
    
    def _graph_expand(
        self,
        seed_nodes: List[Dict[str, Any]],
        hops: int,
    ) -> List[str]:
        """Expand from seed nodes by traversing graph relationships."""
        context_parts = []
        
        for node in seed_nodes[:3]:  # Expand top 3 nodes
            node_name = node["name"]
            
            try:
                subgraph = get_subgraph(node_name, hops)
                
                if subgraph["nodes"]:
                    for n in subgraph["nodes"][:10]:
                        context_parts.append(
                            f"{n.get('type', 'Node')}: {n.get('name', 'Unknown')}"
                        )
                
                if subgraph["edges"]:
                    for e in subgraph["edges"][:10]:
                        context_parts.append(
                            f"{e.get('source', '?')} --[{e.get('type', '?')}]--> "
                            f"{e.get('target', '?')}"
                        )
                        
            except Exception as e:
                logger.debug(f"  Graph expansion failed for {node_name}: {e}")
        
        logger.info(f"  🕸️ Graph expansion found {len(context_parts)} context items")
        return context_parts
    
    def _keyword_graph_search(self, question: str) -> List[str]:
        """Direct graph queries based on keywords in the question."""
        context_parts = []
        question_lower = question.lower()
        
        # Detect supply chain path questions
        if "path" in question_lower or "hop" in question_lower or "reach" in question_lower:
            # Try to find material-to-device paths
            materials = ["Gallium", "Neon", "Cobalt", "Lithium", "Indium", "Germanium",
                        "Rare Earth Elements"]
            devices = ["iPhone 16 Pro", "Samsung Galaxy S25 Ultra", "Google Pixel 9 Pro",
                      "OnePlus 13", "Xiaomi 15 Ultra", "Nothing Phone 3"]
            
            for mat in materials:
                if mat.lower() in question_lower:
                    for dev in devices:
                        if any(w in question_lower for w in dev.lower().split()):
                            path = find_shortest_path(mat, dev)
                            if path:
                                chain = " → ".join(path["supply_chain"])
                                context_parts.append(
                                    f"Path ({path['hops']} hops): {chain}"
                                )
        
        # Detect disruption questions
        if any(w in question_lower for w in ["ban", "restrict", "block", "tariff", "disrupt"]):
            try:
                results = self.conn.execute_and_fetch(
                    "MATCH (re:RiskEvent)-[:DISRUPTS]->(m:Material)"
                    "-[:REQUIRED_FOR]->(c:Component)-[:USED_IN]->(d:Device) "
                    "RETURN re.name AS event, m.name AS material, "
                    "c.name AS component, d.name AS device, "
                    "d.base_price_usd AS price "
                    "LIMIT 20"
                )
                for r in results:
                    context_parts.append(
                        f"Risk chain: {r['event']} disrupts {r['material']} → "
                        f"{r['component']} → {r['device']} (${r['price']})"
                    )
            except Exception:
                pass
        
        # Detect company questions
        if any(w in question_lower for w in ["company", "critical", "important", "powerful"]):
            try:
                results = self.conn.execute_and_fetch(
                    "MATCH (c:Company)-[r:SUPPLIES_TO]->(c2:Company) "
                    "RETURN c.name AS supplier, c2.name AS customer, "
                    "r.contract_value_usd_m AS value "
                    "ORDER BY value DESC LIMIT 10"
                )
                for r in results:
                    context_parts.append(
                        f"Supply: {r['supplier']} → {r['customer']} "
                        f"(${r['value']}M contract)"
                    )
            except Exception:
                pass
        
        # General: Get high-criticality materials
        try:
            results = self.conn.execute_and_fetch(
                "MATCH (m:Material) WHERE m.criticality_score >= 8 "
                "RETURN m.name AS name, m.criticality_score AS score, "
                "m.primary_country AS country, m.export_restricted AS restricted "
                "ORDER BY score DESC"
            )
            for r in results:
                restricted = "RESTRICTED" if r.get("restricted") else "open"
                context_parts.append(
                    f"Critical material: {r['name']} (score: {r['score']}/10, "
                    f"source: {r['country']}, status: {restricted})"
                )
        except Exception:
            pass
        
        logger.info(f"  🔑 Keyword graph search found {len(context_parts)} items")
        return context_parts
    
    def _combine_context(
        self,
        vector_results: List[Dict[str, Any]],
        graph_context: List[str],
        keyword_context: List[str],
        graph_hops: int = 2,
    ) -> Dict[str, Any]:
        """Combine all retrieved context into a structured result."""
        # Build context string
        context_parts = []
        
        # Vector search results
        if vector_results:
            context_parts.append("=== Relevant Nodes (Vector Search) ===")
            for vr in vector_results:
                context_parts.append(vr["text"])
        
        # Graph traversal results
        if graph_context:
            context_parts.append("\n=== Graph Traversal Context ===")
            context_parts.extend(graph_context)
        
        # Keyword graph results
        if keyword_context:
            context_parts.append("\n=== Supply Chain Intelligence ===")
            context_parts.extend(keyword_context)
        
        # Deduplicate
        seen = set()
        unique_parts = []
        for part in context_parts:
            if part not in seen:
                seen.add(part)
                unique_parts.append(part)
        
        context_str = "\n".join(unique_parts)
        
        all_nodes = [vr["name"] for vr in vector_results]
        
        return {
            "context": context_str,
            "nodes": all_nodes,
            "node_count": len(all_nodes),
            "graph_items": len(graph_context),
            "graph_hops": graph_hops if graph_context else 0,
            "keyword_items": len(keyword_context),
            "method": "hybrid_vector_graph",
        }
