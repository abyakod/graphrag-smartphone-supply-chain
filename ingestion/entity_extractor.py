"""
PhoneGraph: Entity & Relationship Extractor

Optional LLM-based entity extraction from unstructured text.
Falls back to rule-based extraction when no API key is available.
Used to enrich the knowledge graph from SEC filings and news articles.
"""

import logging
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Known entity patterns for rule-based extraction
KNOWN_COMPANIES = [
    "TSMC", "ASML", "Apple", "Samsung", "Qualcomm", "SK Hynix", "Micron",
    "Foxconn", "Corning", "Murata", "Texas Instruments", "Intel", "NVIDIA",
    "AMD", "Google", "Kioxia", "Samsung Display", "Samsung Semiconductor",
    "Sony", "TDK", "AAC Technologies", "BOE", "BYD", "ATL",
]

KNOWN_MATERIALS = [
    "Gallium", "Neon", "Cobalt", "Rare Earth Elements", "Lithium",
    "Indium", "Germanium", "Silicon", "Copper", "Gold", "Palladium",
    "Tantalum", "Tungsten", "Tin",
]

KNOWN_COUNTRIES = [
    "China", "Taiwan", "USA", "South Korea", "Japan", "Netherlands",
    "DRC", "Australia", "Chile", "Ukraine", "Russia", "India",
    "Germany", "Belgium", "Philippines", "Canada", "Argentina",
    "Brazil", "Myanmar", "France",
]


def extract_entities_rule_based(text: str) -> Dict[str, List[str]]:
    """
    Extract known entities from text using rule-based matching.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dict with keys: companies, materials, countries
    """
    found_companies = [c for c in KNOWN_COMPANIES if c.lower() in text.lower()]
    found_materials = [m for m in KNOWN_MATERIALS if m.lower() in text.lower()]
    found_countries = [c for c in KNOWN_COUNTRIES if c.lower() in text.lower()]
    
    return {
        "companies": found_companies,
        "materials": found_materials,
        "countries": found_countries,
    }


def extract_relationships_rule_based(
    text: str,
) -> List[Dict[str, str]]:
    """
    Extract supply chain relationships from text using patterns.
    
    Looks for patterns like:
    - "X supplies Y"
    - "X manufactures for Y"
    - "X depends on Y"
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of relationship dicts with: source, target, type
    """
    relationships = []
    
    supply_patterns = [
        (r"(\w+)\s+supplies?\s+(?:to\s+)?(\w+)", "SUPPLIES_TO"),
        (r"(\w+)\s+manufactures?\s+(?:for\s+)?(\w+)", "MANUFACTURES"),
        (r"(\w+)\s+(?:depends?|relies?)\s+on\s+(\w+)", "DEPENDS_ON"),
        (r"(\w+)\s+exports?\s+(?:to\s+)?(\w+)", "EXPORTS_TO"),
        (r"(\w+)\s+(?:bans?|restricts?)\s+(?:export\s+of\s+)?(\w+)", "RESTRICTS"),
    ]
    
    for pattern, rel_type in supply_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            source = match.group(1).strip()
            target = match.group(2).strip()
            
            # Only include if both entities are known
            all_known = KNOWN_COMPANIES + KNOWN_MATERIALS + KNOWN_COUNTRIES
            all_known_lower = [k.lower() for k in all_known]
            
            if (source.lower() in all_known_lower and 
                    target.lower() in all_known_lower):
                relationships.append({
                    "source": source,
                    "target": target,
                    "type": rel_type,
                })
    
    return relationships


def extract_entities_llm(text: str) -> Dict[str, Any]:
    """
    Extract entities and relationships using LLM.
    
    Tries Ollama first (local), then OpenAI (cloud).
    Falls back to rule-based extraction if neither is available.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dict with entities and relationships
    """
    prompt = f"""Extract supply chain entities and relationships from this text.

Return JSON with:
- companies: list of company names
- materials: list of raw material names  
- countries: list of country names
- relationships: list of {{source, target, type}} where type is one of:
  SUPPLIES_TO, MANUFACTURES, REQUIRED_FOR, EXTRACTED_IN, HEADQUARTERED_IN,
  DISRUPTS, AFFECTS, RESTRICTS

Text: {text}

Return ONLY valid JSON, no markdown."""

    # Try Ollama first
    try:
        import os
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        import httpx
        httpx.get(f"{ollama_url}/api/tags", timeout=2).raise_for_status()
        
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model=ollama_model, base_url=ollama_url, temperature=0)
        response = llm.invoke(prompt)
        
        import json
        result = json.loads(response.content)
        logger.info(f"🤖 Ollama extracted {len(result.get('companies', []))} companies, "
                   f"{len(result.get('relationships', []))} relationships")
        return result
    except Exception:
        pass

    # Try OpenAI
    try:
        import os
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key and api_key != "your-openai-api-key-here":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
            response = llm.invoke(prompt)
            
            import json
            result = json.loads(response.content)
            logger.info(f"🤖 OpenAI extracted {len(result.get('companies', []))} companies, "
                       f"{len(result.get('relationships', []))} relationships")
            return result
    except Exception:
        pass

    # Fallback to rules
    logger.info("No LLM available — using rule-based extraction")
    entities = extract_entities_rule_based(text)
    relationships = extract_relationships_rule_based(text)
    return {"entities": entities, "relationships": relationships}


def enrich_from_text(
    text: str, use_llm: bool = False
) -> Tuple[Dict[str, List[str]], List[Dict[str, str]]]:
    """
    Main entry point for entity extraction.
    
    Args:
        text: Input text
        use_llm: Whether to use LLM extraction (requires API key)
        
    Returns:
        Tuple of (entities_dict, relationships_list)
    """
    if use_llm:
        result = extract_entities_llm(text)
        entities = {
            "companies": result.get("companies", []),
            "materials": result.get("materials", []),
            "countries": result.get("countries", []),
        }
        relationships = result.get("relationships", [])
    else:
        entities = extract_entities_rule_based(text)
        relationships = extract_relationships_rule_based(text)
    
    return entities, relationships
