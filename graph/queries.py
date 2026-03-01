"""
PhoneGraph: Named Cypher Query Constants

All Cypher queries organized by category. Used throughout the application
for consistent, optimized database interactions.
"""

# ═══════════════════════════════════════════════════
# Node Creation Queries
# ═══════════════════════════════════════════════════

CREATE_MATERIAL = """
MERGE (m:Material {name: $name})
SET m.type = $type,
    m.annual_production_tons = $annual_production_tons,
    m.criticality_score = $criticality_score,
    m.primary_country = $primary_country,
    m.export_restricted = $export_restricted,
    m.price_usd_per_kg = $price_usd_per_kg
RETURN m
"""

CREATE_COMPANY = """
MERGE (c:Company {name: $name})
SET c.country = $country,
    c.revenue_usd_billions = $revenue_usd_billions,
    c.market_cap_usd_billions = $market_cap_usd_billions,
    c.type = $type,
    c.employees = $employees,
    c.founded_year = $founded_year,
    c.ticker_symbol = $ticker_symbol
RETURN c
"""

CREATE_COMPONENT = """
MERGE (c:Component {name: $name})
SET c.category = $category,
    c.process_node_nm = $process_node_nm,
    c.estimated_cost_usd = $estimated_cost_usd,
    c.lead_time_weeks = $lead_time_weeks,
    c.single_sourced = $single_sourced
RETURN c
"""

CREATE_DEVICE = """
MERGE (d:Device {name: $name})
SET d.brand = $brand,
    d.launch_year = $launch_year,
    d.base_price_usd = $base_price_usd,
    d.units_sold_millions = $units_sold_millions,
    d.market_segment = $market_segment
RETURN d
"""

CREATE_COUNTRY = """
MERGE (c:Country {name: $name})
SET c.iso_code = $iso_code,
    c.region = $region,
    c.geopolitical_risk_score = $geopolitical_risk_score,
    c.trade_restriction_risk = $trade_restriction_risk
RETURN c
"""

CREATE_RISK_EVENT = """
MERGE (r:RiskEvent {name: $name})
SET r.type = $type,
    r.date = $date,
    r.impact_severity = $impact_severity,
    r.description = $description,
    r.source_url = $source_url
RETURN r
"""

CREATE_REGULATION = """
MERGE (r:Regulation {name: $name})
SET r.jurisdiction = $jurisdiction,
    r.effective_date = $effective_date,
    r.affected_materials = $affected_materials,
    r.penalty_description = $penalty_description
RETURN r
"""

# ═══════════════════════════════════════════════════
# Relationship Creation Queries
# ═══════════════════════════════════════════════════

CREATE_REQUIRED_FOR = """
MATCH (m:Material {name: $material_name})
MATCH (c:Component {name: $component_name})
MERGE (m)-[r:REQUIRED_FOR]->(c)
SET r.percentage = $percentage
RETURN r
"""

CREATE_EXTRACTED_IN = """
MATCH (m:Material {name: $material_name})
MATCH (c:Country {name: $country_name})
MERGE (m)-[r:EXTRACTED_IN]->(c)
SET r.percentage = $percentage
RETURN r
"""

CREATE_MANUFACTURES = """
MATCH (co:Company {name: $company_name})
MATCH (c:Component {name: $component_name})
MERGE (co)-[r:MANUFACTURES]->(c)
SET r.capacity_units_per_year = $capacity_units_per_year
RETURN r
"""

CREATE_SUPPLIES_TO = """
MATCH (from:Company {name: $from_company})
MATCH (to:Company {name: $to_company})
MERGE (from)-[r:SUPPLIES_TO]->(to)
SET r.contract_value_usd_m = $contract_value_usd_m
RETURN r
"""

CREATE_HEADQUARTERED_IN = """
MATCH (co:Company {name: $company_name})
MATCH (c:Country {name: $country_name})
MERGE (co)-[r:HEADQUARTERED_IN]->(c)
RETURN r
"""

CREATE_USED_IN = """
MATCH (c:Component {name: $component_name})
MATCH (d:Device {name: $device_name})
MERGE (c)-[r:USED_IN]->(d)
SET r.units_per_device = $units_per_device
RETURN r
"""

CREATE_EXPORTS_TO = """
MATCH (from:Country {name: $from_country})
MATCH (to:Country {name: $to_country})
MERGE (from)-[r:EXPORTS_TO]->(to)
SET r.value_usd_billions = $value_usd_billions,
    r.year = $year
RETURN r
"""

CREATE_DISRUPTS = """
MATCH (re:RiskEvent {name: $event_name})
MATCH (m:Material {name: $material_name})
MERGE (re)-[r:DISRUPTS]->(m)
SET r.severity = $severity
RETURN r
"""

CREATE_AFFECTS = """
MATCH (re:RiskEvent {name: $event_name})
MATCH (c:Company {name: $company_name})
MERGE (re)-[r:AFFECTS]->(c)
RETURN r
"""

CREATE_RESTRICTS = """
MATCH (reg:Regulation {name: $regulation_name})
MATCH (m:Material {name: $material_name})
MERGE (reg)-[r:RESTRICTS]->(m)
RETURN r
"""

# ═══════════════════════════════════════════════════
# Algorithm Queries (using MAGE)
# ═══════════════════════════════════════════════════

PAGERANK_QUERY = """
CALL pagerank.get()
YIELD node, rank
RETURN node.name AS name, labels(node)[0] AS type, rank
ORDER BY rank DESC
LIMIT 20
"""

BETWEENNESS_CENTRALITY_QUERY = """
CALL betweenness_centrality.get(FALSE, FALSE)
YIELD node, betweenness_centrality
RETURN node.name AS name, labels(node)[0] AS type, betweenness_centrality
ORDER BY betweenness_centrality DESC
LIMIT 10
"""

COMMUNITY_DETECTION_QUERY = """
CALL community_detection.get()
YIELD node, community_id
RETURN community_id,
       collect(node.name) AS members,
       count(node) AS size
ORDER BY size DESC
"""

SHORTEST_PATH_QUERY = """
MATCH path = shortestPath(
  (start {name: $start_node})-[*]-(end {name: $end_node})
)
RETURN
  [node IN nodes(path) | node.name] AS supply_chain,
  [node IN nodes(path) | labels(node)[0]] AS node_types,
  length(path) AS hops
"""

# ═══════════════════════════════════════════════════
# Traversal & Analysis Queries
# ═══════════════════════════════════════════════════

# Find all paths from a disrupted node to devices
SHOCK_PROPAGATION_QUERY = """
MATCH path = (start {name: $disrupted_node})-[*1..6]->(d:Device)
WITH d,
     min(length(path)) AS min_hops,
     count(path) AS dependency_paths,
     d.base_price_usd AS current_price
RETURN
    d.name AS device,
    current_price,
    min_hops,
    dependency_paths,
    current_price * (0.15 / min_hops) AS estimated_price_increase
ORDER BY estimated_price_increase DESC
"""

# Get subgraph around a specific node
SUBGRAPH_QUERY = """
MATCH (center {name: $node_name})
MATCH path = (center)-[*1..$hops]-(connected)
WITH DISTINCT connected, center, relationships(path) AS rels
RETURN
    center.name AS center_name,
    labels(center)[0] AS center_type,
    connected.name AS connected_name,
    labels(connected)[0] AS connected_type,
    size(rels) AS distance
LIMIT 100
"""

# Supply chain path from material to device
MATERIAL_TO_DEVICE_PATH = """
MATCH path = (m:Material {name: $material_name})-[*]->(d:Device)
WHERE all(r IN relationships(path) WHERE
    type(r) IN ['REQUIRED_FOR', 'MANUFACTURES', 'SUPPLIES_TO', 'USED_IN'])
RETURN
    [node IN nodes(path) | node.name] AS chain,
    [node IN nodes(path) | labels(node)[0]] AS types,
    length(path) AS hops
ORDER BY hops ASC
LIMIT 5
"""

# Count all nodes and relationships
GRAPH_STATS_QUERY = """
MATCH (n)
WITH count(n) AS total_nodes
MATCH ()-[r]->()
WITH total_nodes, count(r) AS total_edges
RETURN total_nodes, total_edges
"""

# Get all nodes with their labels
ALL_NODES_QUERY = """
MATCH (n)
RETURN
    id(n) AS id,
    labels(n)[0] AS type,
    n.name AS name,
    properties(n) AS properties
ORDER BY type, name
"""

# Get all relationships
ALL_RELATIONSHIPS_QUERY = """
MATCH (a)-[r]->(b)
RETURN
    id(r) AS id,
    a.name AS source,
    labels(a)[0] AS source_type,
    type(r) AS relationship,
    b.name AS target,
    labels(b)[0] AS target_type,
    properties(r) AS properties
"""

# Devices affected by a material disruption
MATERIAL_IMPACT_QUERY = """
MATCH (m:Material {name: $material_name})-[:REQUIRED_FOR]->(comp:Component)-[:USED_IN]->(d:Device)
RETURN d.name AS device, d.base_price_usd AS price,
       comp.name AS component, comp.single_sourced AS single_sourced
"""

# Companies dependent on a specific country
COUNTRY_DEPENDENCY_QUERY = """
MATCH (c:Company)-[:HEADQUARTERED_IN]->(country:Country {name: $country_name})
RETURN c.name AS company, c.type AS type, c.revenue_usd_billions AS revenue
UNION
MATCH (m:Material)-[:EXTRACTED_IN]->(country:Country {name: $country_name})
RETURN m.name AS company, 'material_source' AS type, m.criticality_score AS revenue
"""

# Risk events timeline
RISK_TIMELINE_QUERY = """
MATCH (re:RiskEvent)
OPTIONAL MATCH (re)-[:DISRUPTS]->(m:Material)
OPTIONAL MATCH (re)-[:AFFECTS]->(c:Company)
RETURN re.name AS event, re.date AS date, re.impact_severity AS severity,
       re.type AS event_type,
       collect(DISTINCT m.name) AS disrupted_materials,
       collect(DISTINCT c.name) AS affected_companies
ORDER BY re.date DESC
"""
