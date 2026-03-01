"""
PhoneGraph: Master Graph Builder

Orchestrates the complete ingestion pipeline:
1. Clear existing graph
2. Create schema (indexes)
3. Ingest all 7 node types from real data
4. Create all 10 relationship types
5. Verify with counts

Run with: python -m ingestion.graph_builder
"""

import logging
import sys
from typing import Any, Dict

from graph.connection import get_connection
from graph.schema import create_schema
from ingestion.usgs_fetcher import fetch_minerals
from ingestion.comtrade_fetcher import fetch_trade_flows, fetch_countries
from ingestion.sec_fetcher import (
    fetch_companies,
    fetch_devices,
    fetch_risk_events,
    fetch_regulations,
    fetch_supply_relationships,
    get_component_materials,
    COMPONENT_MATERIALS,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def escape_cypher_string(value: str) -> str:
    """Escape single quotes and backslashes for Cypher string literals."""
    if value is None:
        return ""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


class GraphBuilder:
    """
    Master orchestrator for building the PhoneGraph knowledge graph.
    
    Coordinates all data fetchers and creates the complete supply chain
    graph in Memgraph with 7 node types and 10 relationship types.
    """
    
    def __init__(self) -> None:
        self.conn = get_connection()
        self.stats: Dict[str, int] = {}
    
    def build(self, clear_first: bool = True) -> Dict[str, int]:
        """
        Execute the complete ingestion pipeline.
        
        Args:
            clear_first: Whether to clear existing data before building
            
        Returns:
            Dictionary with counts of created nodes and relationships
        """
        logger.info("═" * 55)
        logger.info("🚀 PhoneGraph: Building Supply Chain Knowledge Graph")
        logger.info("═" * 55)
        
        if clear_first:
            self.conn.clear_database()
        
        # Step 1: Create schema
        create_schema()
        
        # Step 2: Ingest all node types
        self._ingest_countries()
        self._ingest_materials()
        self._ingest_companies()
        self._ingest_components()
        self._ingest_devices()
        self._ingest_risk_events()
        self._ingest_regulations()
        
        # Step 3: Create all relationship types
        self._create_extracted_in_relationships()
        self._create_headquartered_in_relationships()
        self._create_supplies_to_relationships()
        self._create_manufactures_relationships()
        self._create_required_for_relationships()
        self._create_used_in_relationships()
        self._create_exports_to_relationships()
        self._create_disrupts_relationships()
        self._create_affects_relationships()
        self._create_restricts_relationships()
        
        # Step 4: Verify
        self._verify_graph()
        
        logger.info("═" * 55)
        logger.info("✅ PhoneGraph Knowledge Graph Built Successfully!")
        logger.info("═" * 55)
        
        return self.stats
    
    # ─── Node Ingestion ───────────────────────────────
    
    def _ingest_countries(self) -> None:
        """Ingest all country nodes."""
        countries = fetch_countries()
        logger.info(f"🌍 Ingesting {len(countries)} countries...")
        
        count = 0
        for name, data in countries.items():
            query = f"""
            MERGE (c:Country {{name: '{escape_cypher_string(name)}'}})
            SET c.iso_code = '{escape_cypher_string(data.get('iso_code', ''))}',
                c.region = '{escape_cypher_string(data.get('region', ''))}',
                c.geopolitical_risk_score = {data.get('geopolitical_risk_score', 5)},
                c.trade_restriction_risk = {data.get('trade_restriction_risk', 5)}
            """
            self.conn.execute(query)
            count += 1
        
        self.stats["countries"] = count
        logger.info(f"  ✓ Created {count} Country nodes")
    
    def _ingest_materials(self) -> None:
        """Ingest all material nodes."""
        minerals = fetch_minerals()
        logger.info(f"⚗️ Ingesting {len(minerals)} materials...")
        
        count = 0
        for name, data in minerals.items():
            export_restricted = "true" if data.get("export_restricted", False) else "false"
            query = f"""
            MERGE (m:Material {{name: '{escape_cypher_string(name)}'}})
            SET m.type = '{escape_cypher_string(data.get('type', 'metal'))}',
                m.annual_production_tons = {data.get('annual_production_tons', 0)},
                m.criticality_score = {data.get('criticality_score', 5)},
                m.primary_country = '{escape_cypher_string(data.get('primary_country', ''))}',
                m.export_restricted = {export_restricted},
                m.price_usd_per_kg = {data.get('price_usd_per_kg', 0)}
            """
            self.conn.execute(query)
            count += 1
        
        self.stats["materials"] = count
        logger.info(f"  ✓ Created {count} Material nodes")
    
    def _ingest_companies(self) -> None:
        """Ingest all company nodes."""
        companies = fetch_companies()
        logger.info(f"🏢 Ingesting {len(companies)} companies...")
        
        count = 0
        for name, data in companies.items():
            market_cap = data.get("market_cap_usd_billions")
            market_cap_val = f"{market_cap}" if market_cap is not None else "0"
            ticker = data.get("ticker_symbol")
            ticker_val = f"'{escape_cypher_string(ticker)}'" if ticker else "''"
            
            query = f"""
            MERGE (c:Company {{name: '{escape_cypher_string(name)}'}})
            SET c.country = '{escape_cypher_string(data.get('country', ''))}',
                c.revenue_usd_billions = {data.get('revenue_usd_billions', 0)},
                c.market_cap_usd_billions = {market_cap_val},
                c.type = '{escape_cypher_string(data.get('type', ''))}',
                c.employees = {data.get('employees', 0)},
                c.founded_year = {data.get('founded_year', 0)},
                c.ticker_symbol = {ticker_val}
            """
            self.conn.execute(query)
            count += 1
        
        self.stats["companies"] = count
        logger.info(f"  ✓ Created {count} Company nodes")
    
    def _ingest_components(self) -> None:
        """Ingest all component nodes from device teardown data."""
        devices = fetch_devices()
        logger.info("🔧 Ingesting components from device teardowns...")
        
        components_seen = set()
        count = 0
        
        for device_name, device_data in devices.items():
            for comp_name, comp_data in device_data.get("components", {}).items():
                if comp_name in components_seen:
                    continue
                components_seen.add(comp_name)
                
                process_nm = comp_data.get("process_nm")
                process_val = f"{process_nm}" if process_nm is not None else "0"
                single_sourced = "true" if comp_data.get("single_sourced", False) else "false"
                
                query = f"""
                MERGE (c:Component {{name: '{escape_cypher_string(comp_name)}'}})
                SET c.category = '{escape_cypher_string(comp_data.get('category', ''))}',
                    c.process_node_nm = {process_val},
                    c.estimated_cost_usd = {comp_data.get('cost_usd', 0)},
                    c.lead_time_weeks = 12,
                    c.single_sourced = {single_sourced}
                """
                self.conn.execute(query)
                count += 1
        
        self.stats["components"] = count
        logger.info(f"  ✓ Created {count} Component nodes")
    
    def _ingest_devices(self) -> None:
        """Ingest all device nodes."""
        devices = fetch_devices()
        logger.info(f"📱 Ingesting {len(devices)} devices...")
        
        count = 0
        for name, data in devices.items():
            query = f"""
            MERGE (d:Device {{name: '{escape_cypher_string(name)}'}})
            SET d.brand = '{escape_cypher_string(data.get('brand', ''))}',
                d.launch_year = {data.get('launch_year', 2024)},
                d.base_price_usd = {data.get('base_price_usd', 0)},
                d.units_sold_millions = {data.get('units_sold_millions', 0)},
                d.market_segment = '{escape_cypher_string(data.get('market_segment', ''))}'
            """
            self.conn.execute(query)
            count += 1
        
        self.stats["devices"] = count
        logger.info(f"  ✓ Created {count} Device nodes")
    
    def _ingest_risk_events(self) -> None:
        """Ingest all risk event nodes."""
        events = fetch_risk_events()
        logger.info(f"⚠️ Ingesting {len(events)} risk events...")
        
        count = 0
        for event in events:
            query = f"""
            MERGE (r:RiskEvent {{name: '{escape_cypher_string(event['name'])}'}})
            SET r.type = '{escape_cypher_string(event.get('type', ''))}',
                r.date = '{escape_cypher_string(event.get('date', ''))}',
                r.impact_severity = {event.get('impact_severity', 5)},
                r.description = '{escape_cypher_string(event.get('description', ''))}',
                r.source_url = '{escape_cypher_string(event.get('source_url', ''))}'
            """
            self.conn.execute(query)
            count += 1
        
        self.stats["risk_events"] = count
        logger.info(f"  ✓ Created {count} RiskEvent nodes")
    
    def _ingest_regulations(self) -> None:
        """Ingest all regulation nodes."""
        regulations = fetch_regulations()
        logger.info(f"📜 Ingesting {len(regulations)} regulations...")
        
        count = 0
        for reg in regulations:
            affected = ", ".join(reg.get("affected_materials", []))
            query = f"""
            MERGE (r:Regulation {{name: '{escape_cypher_string(reg['name'])}'}})
            SET r.jurisdiction = '{escape_cypher_string(reg.get('jurisdiction', ''))}',
                r.effective_date = '{escape_cypher_string(reg.get('effective_date', ''))}',
                r.affected_materials = '{escape_cypher_string(affected)}',
                r.penalty_description = '{escape_cypher_string(reg.get('penalty_description', ''))}'
            """
            self.conn.execute(query)
            count += 1
        
        self.stats["regulations"] = count
        logger.info(f"  ✓ Created {count} Regulation nodes")
    
    # ─── Relationship Creation ────────────────────────
    
    def _create_extracted_in_relationships(self) -> None:
        """Create Material -[:EXTRACTED_IN]-> Country relationships."""
        minerals = fetch_minerals()
        logger.info("🔗 Creating EXTRACTED_IN relationships...")
        
        count = 0
        for mineral_name, data in minerals.items():
            for country, pct in data.get("extraction_countries", {}).items():
                query = f"""
                MATCH (m:Material {{name: '{escape_cypher_string(mineral_name)}'}})
                MATCH (c:Country {{name: '{escape_cypher_string(country)}'}})
                MERGE (m)-[r:EXTRACTED_IN]->(c)
                SET r.percentage = {pct}
                """
                try:
                    self.conn.execute(query)
                    count += 1
                except Exception as e:
                    logger.debug(f"  Skipped: {mineral_name} -> {country}: {e}")
        
        self.stats["extracted_in"] = count
        logger.info(f"  ✓ Created {count} EXTRACTED_IN relationships")
    
    def _create_headquartered_in_relationships(self) -> None:
        """Create Company -[:HEADQUARTERED_IN]-> Country relationships."""
        companies = fetch_companies()
        logger.info("🔗 Creating HEADQUARTERED_IN relationships...")
        
        count = 0
        for company_name, data in companies.items():
            country = data.get("country", "")
            if country:
                query = f"""
                MATCH (co:Company {{name: '{escape_cypher_string(company_name)}'}})
                MATCH (c:Country {{name: '{escape_cypher_string(country)}'}})
                MERGE (co)-[r:HEADQUARTERED_IN]->(c)
                """
                try:
                    self.conn.execute(query)
                    count += 1
                except Exception as e:
                    logger.debug(f"  Skipped: {company_name} -> {country}: {e}")
        
        self.stats["headquartered_in"] = count
        logger.info(f"  ✓ Created {count} HEADQUARTERED_IN relationships")
    
    def _create_supplies_to_relationships(self) -> None:
        """Create Company -[:SUPPLIES_TO]-> Company relationships."""
        relationships = fetch_supply_relationships()
        logger.info("🔗 Creating SUPPLIES_TO relationships...")
        
        count = 0
        for rel in relationships:
            query = f"""
            MATCH (from:Company {{name: '{escape_cypher_string(rel['from'])}'}})
            MATCH (to:Company {{name: '{escape_cypher_string(rel['to'])}'}})
            MERGE (from)-[r:SUPPLIES_TO]->(to)
            SET r.contract_value_usd_m = {rel.get('contract_value_usd_m', 0)}
            """
            try:
                self.conn.execute(query)
                count += 1
            except Exception as e:
                logger.debug(f"  Skipped: {rel['from']} -> {rel['to']}: {e}")
        
        self.stats["supplies_to"] = count
        logger.info(f"  ✓ Created {count} SUPPLIES_TO relationships")
    
    def _create_manufactures_relationships(self) -> None:
        """Create Company -[:MANUFACTURES]-> Component relationships."""
        devices = fetch_devices()
        logger.info("🔗 Creating MANUFACTURES relationships...")
        
        count = 0
        seen = set()
        
        for device_name, device_data in devices.items():
            for comp_name, comp_data in device_data.get("components", {}).items():
                manufacturer = comp_data.get("manufacturer", "")
                key = (manufacturer, comp_name)
                if key in seen or not manufacturer:
                    continue
                seen.add(key)
                
                query = f"""
                MATCH (co:Company {{name: '{escape_cypher_string(manufacturer)}'}})
                MATCH (c:Component {{name: '{escape_cypher_string(comp_name)}'}})
                MERGE (co)-[r:MANUFACTURES]->(c)
                SET r.capacity_units_per_year = 500000000
                """
                try:
                    self.conn.execute(query)
                    count += 1
                except Exception as e:
                    logger.debug(f"  Skipped: {manufacturer} -> {comp_name}: {e}")
        
        self.stats["manufactures"] = count
        logger.info(f"  ✓ Created {count} MANUFACTURES relationships")
    
    def _create_required_for_relationships(self) -> None:
        """Create Material -[:REQUIRED_FOR]-> Component relationships."""
        devices = fetch_devices()
        component_materials = get_component_materials()
        logger.info("🔗 Creating REQUIRED_FOR relationships...")
        
        count = 0
        seen = set()
        
        for device_name, device_data in devices.items():
            for comp_name, comp_data in device_data.get("components", {}).items():
                category = comp_data.get("category", "")
                materials = component_materials.get(category, {})
                
                for material_name, pct in materials.items():
                    key = (material_name, comp_name)
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    query = f"""
                    MATCH (m:Material {{name: '{escape_cypher_string(material_name)}'}})
                    MATCH (c:Component {{name: '{escape_cypher_string(comp_name)}'}})
                    MERGE (m)-[r:REQUIRED_FOR]->(c)
                    SET r.percentage = {pct}
                    """
                    try:
                        self.conn.execute(query)
                        count += 1
                    except Exception as e:
                        logger.debug(f"  Skipped: {material_name} -> {comp_name}: {e}")
        
        self.stats["required_for"] = count
        logger.info(f"  ✓ Created {count} REQUIRED_FOR relationships")
    
    def _create_used_in_relationships(self) -> None:
        """Create Component -[:USED_IN]-> Device relationships."""
        devices = fetch_devices()
        logger.info("🔗 Creating USED_IN relationships...")
        
        count = 0
        for device_name, device_data in devices.items():
            for comp_name, comp_data in device_data.get("components", {}).items():
                query = f"""
                MATCH (c:Component {{name: '{escape_cypher_string(comp_name)}'}})
                MATCH (d:Device {{name: '{escape_cypher_string(device_name)}'}})
                MERGE (c)-[r:USED_IN]->(d)
                SET r.units_per_device = 1
                """
                try:
                    self.conn.execute(query)
                    count += 1
                except Exception as e:
                    logger.debug(f"  Skipped: {comp_name} -> {device_name}: {e}")
        
        self.stats["used_in"] = count
        logger.info(f"  ✓ Created {count} USED_IN relationships")
    
    def _create_exports_to_relationships(self) -> None:
        """Create Country -[:EXPORTS_TO]-> Country relationships."""
        trade_flows = fetch_trade_flows()
        logger.info("🔗 Creating EXPORTS_TO relationships...")
        
        count = 0
        for flow in trade_flows:
            query = f"""
            MATCH (from:Country {{name: '{escape_cypher_string(flow['from'])}'}})
            MATCH (to:Country {{name: '{escape_cypher_string(flow['to'])}'}})
            MERGE (from)-[r:EXPORTS_TO]->(to)
            SET r.value_usd_billions = {flow.get('value_usd_billions', 0)},
                r.year = {flow.get('year', 2023)}
            """
            try:
                self.conn.execute(query)
                count += 1
            except Exception as e:
                logger.debug(f"  Skipped: {flow['from']} -> {flow['to']}: {e}")
        
        self.stats["exports_to"] = count
        logger.info(f"  ✓ Created {count} EXPORTS_TO relationships")
    
    def _create_disrupts_relationships(self) -> None:
        """Create RiskEvent -[:DISRUPTS]-> Material relationships."""
        events = fetch_risk_events()
        logger.info("🔗 Creating DISRUPTS relationships...")
        
        count = 0
        for event in events:
            for material in event.get("affected_materials", []):
                query = f"""
                MATCH (re:RiskEvent {{name: '{escape_cypher_string(event['name'])}'}})
                MATCH (m:Material {{name: '{escape_cypher_string(material)}'}})
                MERGE (re)-[r:DISRUPTS]->(m)
                SET r.severity = {event.get('impact_severity', 5)}
                """
                try:
                    self.conn.execute(query)
                    count += 1
                except Exception as e:
                    logger.debug(f"  Skipped: {event['name']} -> {material}: {e}")
        
        self.stats["disrupts"] = count
        logger.info(f"  ✓ Created {count} DISRUPTS relationships")
    
    def _create_affects_relationships(self) -> None:
        """Create RiskEvent -[:AFFECTS]-> Company relationships."""
        events = fetch_risk_events()
        logger.info("🔗 Creating AFFECTS relationships...")
        
        count = 0
        for event in events:
            for company in event.get("affected_companies", []):
                query = f"""
                MATCH (re:RiskEvent {{name: '{escape_cypher_string(event['name'])}'}})
                MATCH (c:Company {{name: '{escape_cypher_string(company)}'}})
                MERGE (re)-[r:AFFECTS]->(c)
                """
                try:
                    self.conn.execute(query)
                    count += 1
                except Exception as e:
                    logger.debug(f"  Skipped: {event['name']} -> {company}: {e}")
        
        self.stats["affects"] = count
        logger.info(f"  ✓ Created {count} AFFECTS relationships")
    
    def _create_restricts_relationships(self) -> None:
        """Create Regulation -[:RESTRICTS]-> Material relationships."""
        regulations = fetch_regulations()
        logger.info("🔗 Creating RESTRICTS relationships...")
        
        count = 0
        for reg in regulations:
            for material in reg.get("affected_materials", []):
                query = f"""
                MATCH (r:Regulation {{name: '{escape_cypher_string(reg['name'])}'}})
                MATCH (m:Material {{name: '{escape_cypher_string(material)}'}})
                MERGE (r)-[rel:RESTRICTS]->(m)
                """
                try:
                    self.conn.execute(query)
                    count += 1
                except Exception as e:
                    logger.debug(f"  Skipped: {reg['name']} -> {material}: {e}")
        
        self.stats["restricts"] = count
        logger.info(f"  ✓ Created {count} RESTRICTS relationships")
    
    # ─── Verification ─────────────────────────────────
    
    def _verify_graph(self) -> None:
        """Verify the graph was built correctly by counting nodes and edges."""
        logger.info("\n📊 Graph Verification:")
        logger.info("─" * 40)
        
        # Count total nodes
        result = self.conn.execute_and_fetch(
            "MATCH (n) RETURN count(n) AS count"
        )
        total_nodes = result[0]["count"] if result else 0
        
        # Count total relationships
        result = self.conn.execute_and_fetch(
            "MATCH ()-[r]->() RETURN count(r) AS count"
        )
        total_edges = result[0]["count"] if result else 0
        
        # Count by label
        label_counts = self.conn.execute_and_fetch(
            "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count "
            "ORDER BY count DESC"
        )
        
        for lc in label_counts:
            logger.info(f"  {lc['label']}: {lc['count']} nodes")
        
        # Count by relationship type
        rel_counts = self.conn.execute_and_fetch(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count "
            "ORDER BY count DESC"
        )
        
        for rc in rel_counts:
            logger.info(f"  {rc['type']}: {rc['count']} relationships")
        
        logger.info("─" * 40)
        logger.info(f"  TOTAL: {total_nodes} nodes, {total_edges} relationships")
        
        self.stats["total_nodes"] = total_nodes
        self.stats["total_edges"] = total_edges


def main() -> None:
    """Main entry point for graph building."""
    builder = GraphBuilder()
    stats = builder.build()
    
    print("\n📈 Build Summary:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
