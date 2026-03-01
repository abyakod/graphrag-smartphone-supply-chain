"""
PhoneGraph: Graph Visualization Component

Generates interactive Pyvis network visualizations
with a clean dark theme matching the dashboard design.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Color palette for node types — cohesive, accessible on dark backgrounds
NODE_COLORS = {
    "Material": "#FF6B9D",
    "Company": "#7B68EE",
    "Component": "#00D4FF",
    "Device": "#FFD93D",
    "Country": "#00FF88",
    "RiskEvent": "#FF8C42",
    "Regulation": "#B388FF",
}

NODE_SIZES = {
    "Material": 28,
    "Company": 35,
    "Component": 22,
    "Device": 40,
    "Country": 32,
    "RiskEvent": 24,
    "Regulation": 24,
}


def create_graph_html(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    height: str = "600px",
    physics: bool = True,
) -> str:
    """
    Create an interactive Pyvis graph visualization as HTML.

    Args:
        nodes: List of node dicts with keys: name, type, properties
        edges: List of edge dicts with keys: source, target, type
        height: Height of the visualization
        physics: Whether to enable physics simulation

    Returns:
        HTML string of the interactive graph
    """
    try:
        from pyvis.network import Network
    except ImportError:
        return _fallback_html(nodes, edges)

    net = Network(
        height=height,
        width="100%",
        bgcolor="#0A1628",
        font_color="#E2E8F0",
        directed=True,
    )

    # Configure physics
    if physics:
        net.force_atlas_2based(
            gravity=-50,
            central_gravity=0.01,
            spring_length=200,
            spring_strength=0.08,
        )
    else:
        net.toggle_physics(False)

    # Add nodes
    seen_nodes = set()
    for node in nodes:
        name = node.get("name", "Unknown")
        if name in seen_nodes:
            continue
        seen_nodes.add(name)

        node_type = node.get("type", "Unknown")
        color = NODE_COLORS.get(node_type, "#484F58")
        size = NODE_SIZES.get(node_type, 20)

        # Build tooltip
        props = node.get("properties", {})
        tooltip_parts = [f"<b>{name}</b>", f"Type: {node_type}"]
        for key, val in props.items():
            if key != "name":
                tooltip_parts.append(f"{key}: {val}")
        tooltip = "<br>".join(tooltip_parts)

        net.add_node(
            name,
            label=name,
            color=color,
            size=size,
            title=tooltip,
            shape="dot",
            font={"size": 12, "color": "#E6EDF3"},
        )

    # Add edges
    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")
        rel_type = edge.get("type", "")

        if source in seen_nodes and target in seen_nodes:
            net.add_edge(
                source,
                target,
                title=rel_type,
                label=rel_type,
                color="#1A3050",
                width=1.5,
                arrows="to",
                font={"size": 9, "color": "#4A6A85", "align": "middle"},
            )

    # Generate HTML
    html = net.generate_html()
    return html


def _fallback_html(
    nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]
) -> str:
    """Generate a clean HTML table when Pyvis is not available."""
    rows = []
    for node in nodes:
        ntype = node.get("type", "?")
        color = NODE_COLORS.get(ntype, "#484F58")
        rows.append(
            f'<tr><td style="color:{color};">●</td>'
            f'<td>{node.get("name", "?")}</td>'
            f'<td style="color:#484F58;">{ntype}</td></tr>'
        )

    edge_rows = []
    for edge in edges:
        edge_rows.append(
            f'<tr><td>{edge.get("source", "?")}</td>'
            f'<td style="color:#484F58;">{edge.get("type", "?")}</td>'
            f'<td>{edge.get("target", "?")}</td></tr>'
        )

    return f"""
    <div style="background: #0D1117; padding: 2rem; border-radius: 12px; color: #E6EDF3;
                font-family: Inter, -apple-system, sans-serif;">
        <h3 style="color: #6C63FF; margin-bottom: 1rem;">Graph Data</h3>
        <p style="color: #8B949E; font-size: 0.85rem; margin-bottom: 1rem;">
            Install pyvis for interactive visualization: <code>pip install pyvis</code>
        </p>
        <h4 style="color: #E6EDF3;">Nodes ({len(nodes)})</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #21262D;">
                <th style="width: 20px;"></th><th style="text-align:left; padding: 8px;">Name</th>
                <th style="text-align:left; padding: 8px;">Type</th>
            </tr>
            {''.join(rows)}
        </table>
        <h4 style="color: #E6EDF3; margin-top: 1.5rem;">Edges ({len(edges)})</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #21262D;">
                <th style="text-align:left; padding: 8px;">Source</th>
                <th style="text-align:left; padding: 8px;">Type</th>
                <th style="text-align:left; padding: 8px;">Target</th>
            </tr>
            {''.join(edge_rows)}
        </table>
    </div>
    """
