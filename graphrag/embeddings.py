"""
PhoneGraph: Node Embedding Pipeline

Creates text representations of graph nodes and generates embeddings
for vector similarity search. Enables hybrid retrieval combining
vector search with graph traversal.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from graph.connection import get_connection

logger = logging.getLogger(__name__)


def node_to_text(name: str, label: str, properties: Dict[str, Any]) -> str:
    """
    Convert a graph node to a text representation for embedding.
    
    Args:
        name: Node name
        label: Node label (Material, Company, etc.)
        properties: Node properties dictionary
        
    Returns:
        Human-readable text description of the node
    """
    parts = [f"{label}: {name}"]
    
    if label == "Material":
        parts.append(f"Type: {properties.get('type', 'unknown')}")
        parts.append(f"Annual production: {properties.get('annual_production_tons', 'N/A')} tons")
        parts.append(f"Primary country: {properties.get('primary_country', 'N/A')}")
        parts.append(f"Criticality score: {properties.get('criticality_score', 'N/A')}/10")
        parts.append(f"Price: ${properties.get('price_usd_per_kg', 'N/A')}/kg")
        if properties.get("export_restricted"):
            parts.append("⚠️ EXPORT RESTRICTED")
    
    elif label == "Company":
        parts.append(f"Country: {properties.get('country', 'N/A')}")
        parts.append(f"Type: {properties.get('type', 'N/A')}")
        parts.append(f"Revenue: ${properties.get('revenue_usd_billions', 'N/A')}B")
        parts.append(f"Employees: {properties.get('employees', 'N/A')}")
    
    elif label == "Component":
        parts.append(f"Category: {properties.get('category', 'N/A')}")
        if properties.get("process_node_nm"):
            parts.append(f"Process: {properties['process_node_nm']}nm")
        parts.append(f"Cost: ${properties.get('estimated_cost_usd', 'N/A')}")
        if properties.get("single_sourced"):
            parts.append("⚠️ SINGLE-SOURCED")
    
    elif label == "Device":
        parts.append(f"Brand: {properties.get('brand', 'N/A')}")
        parts.append(f"Launch: {properties.get('launch_year', 'N/A')}")
        parts.append(f"Price: ${properties.get('base_price_usd', 'N/A')}")
        parts.append(f"Segment: {properties.get('market_segment', 'N/A')}")
    
    elif label == "Country":
        parts.append(f"Region: {properties.get('region', 'N/A')}")
        parts.append(f"Geopolitical risk: {properties.get('geopolitical_risk_score', 'N/A')}/10")
        parts.append(f"Trade restriction risk: {properties.get('trade_restriction_risk', 'N/A')}/10")
    
    elif label == "RiskEvent":
        parts.append(f"Type: {properties.get('type', 'N/A')}")
        parts.append(f"Date: {properties.get('date', 'N/A')}")
        parts.append(f"Severity: {properties.get('impact_severity', 'N/A')}/10")
        parts.append(f"Description: {properties.get('description', 'N/A')}")
    
    elif label == "Regulation":
        parts.append(f"Jurisdiction: {properties.get('jurisdiction', 'N/A')}")
        parts.append(f"Effective: {properties.get('effective_date', 'N/A')}")
    
    return " | ".join(parts)


def get_all_node_texts() -> List[Dict[str, str]]:
    """
    Get text representations of all nodes in the graph.
    
    Returns:
        List of dicts with keys: name, label, text
    """
    conn = get_connection()
    
    results = conn.execute_and_fetch(
        "MATCH (n) RETURN n.name AS name, labels(n)[0] AS label, "
        "properties(n) AS props"
    )
    
    texts = []
    for r in results:
        text = node_to_text(r["name"], r["label"], r["props"])
        texts.append({
            "name": r["name"],
            "label": r["label"],
            "text": text,
        })
    
    logger.info(f"📝 Generated text for {len(texts)} nodes")
    return texts


def generate_embeddings(texts: List[str]) -> Optional[List[List[float]]]:
    """
    Generate embeddings for a list of texts using OpenAI.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors, or None if API unavailable
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-openai-api-key-here":
        logger.warning("⚠️ No OpenAI API key — embeddings not available")
        return None
    
    try:
        from langchain_openai import OpenAIEmbeddings
        
        embedder = OpenAIEmbeddings(model="text-embedding-3-small")
        embeddings = embedder.embed_documents(texts)
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings "
                    f"(dim={len(embeddings[0])})")
        return embeddings
        
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        return None


def build_embedding_index() -> Optional[Dict[str, Any]]:
    """
    Build an in-memory embedding index for all graph nodes.
    
    Returns:
        Dict with keys: texts, embeddings, names, labels
        or None if embeddings unavailable
    """
    node_texts = get_all_node_texts()
    
    if not node_texts:
        logger.warning("No nodes found in graph")
        return None
    
    texts = [nt["text"] for nt in node_texts]
    embeddings = generate_embeddings(texts)
    
    if embeddings is None:
        return None
    
    return {
        "texts": texts,
        "embeddings": embeddings,
        "names": [nt["name"] for nt in node_texts],
        "labels": [nt["label"] for nt in node_texts],
    }


def find_similar_nodes(
    query: str, index: Dict[str, Any], top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Find the most similar nodes to a query using cosine similarity.
    
    Args:
        query: Search query text
        index: Embedding index from build_embedding_index()
        top_k: Number of results to return
        
    Returns:
        List of dicts with keys: name, label, text, similarity
    """
    try:
        from langchain_openai import OpenAIEmbeddings
        import numpy as np
        
        embedder = OpenAIEmbeddings(model="text-embedding-3-small")
        query_embedding = embedder.embed_query(query)
        
        # Cosine similarity
        query_vec = np.array(query_embedding)
        doc_vecs = np.array(index["embeddings"])
        
        similarities = np.dot(doc_vecs, query_vec) / (
            np.linalg.norm(doc_vecs, axis=1) * np.linalg.norm(query_vec)
        )
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "name": index["names"][idx],
                "label": index["labels"][idx],
                "text": index["texts"][idx],
                "similarity": float(similarities[idx]),
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        return []
