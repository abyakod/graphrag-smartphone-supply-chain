"""
PhoneGraph: Graph Explorer Page — Blue Premium Theme

Interactive graph visualization with path finder.
"""

import sys
sys.path.insert(0, ".")

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Graph Explorer — PhoneGraph", page_icon="🕸️", layout="wide")

# ═══════════════════════════════════════════════════
# Page Header
# ═══════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem;
               background: linear-gradient(135deg, #00FF88, #00D4FF);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🕸️ Graph Explorer
    </h1>
    <p style="color: #4A6A85; font-size: 0.95rem; margin: 0;">
        Explore the supply chain knowledge graph interactively. Click nodes for details, drag to rearrange.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Controls
# ═══════════════════════════════════════════════════

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    center_node = st.text_input("Center on node", value="TSMC", label_visibility="collapsed",
                                 help="Name of any node in the graph")

with col2:
    hops = st.slider("Hops", 1, 4, 2)

with col3:
    physics = st.checkbox("Physics", value=True)

# Quick explore
st.markdown('<p style="color: #4A6A85; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">Quick Explore</p>', unsafe_allow_html=True)
quick_nodes = ["TSMC", "Apple", "Gallium", "iPhone 16 Pro", "China"]
qcols = st.columns(len(quick_nodes))
for i, node in enumerate(quick_nodes):
    with qcols[i]:
        if st.button(node, key=f"quick_{i}", use_container_width=True):
            center_node = node

# ═══════════════════════════════════════════════════
# Graph Visualization
# ═══════════════════════════════════════════════════

if st.button("🕸️ Explore Graph", type="primary", use_container_width=True) or center_node:
    with st.spinner(f"Loading subgraph around {center_node}…"):
        try:
            from graph.algorithms import get_subgraph
            from dashboard.components.graph_viz import create_graph_html, NODE_COLORS

            subgraph = get_subgraph(center_node, hops)

            nodes = subgraph.get("nodes", [])
            edges = subgraph.get("edges", [])

            if nodes:
                # Stats and legend
                s1, s2, s3, _, l1 = st.columns([1, 1, 1, 0.5, 3])
                with s1:
                    st.metric("Nodes", len(nodes))
                with s2:
                    st.metric("Edges", len(edges))
                with s3:
                    node_types = set(n.get("type", "") for n in nodes)
                    st.metric("Types", len(node_types))
                with l1:
                    legend_html = " ".join(
                        f'<span style="color: {color}; font-size: 0.8rem; margin-right: 14px; font-weight: 500;">'
                        f'● {label}</span>'
                        for label, color in NODE_COLORS.items()
                    )
                    st.markdown(f'<div style="padding-top: 0.75rem;">{legend_html}</div>',
                               unsafe_allow_html=True)

                # Graph
                html = create_graph_html(nodes, edges, height="600px", physics=physics)
                components.html(html, height=650, scrolling=True)

                # Node list
                with st.expander(f"📋 All nodes in subgraph ({len(nodes)})"):
                    for n in sorted(nodes, key=lambda x: x.get("type", "")):
                        ntype = n.get("type", "?")
                        color = NODE_COLORS.get(ntype, "#7EB8D8")
                        st.markdown(
                            f'<span style="color: {color};">●</span> '
                            f'<span style="color: #4A6A85; font-size: 0.8rem;">[{ntype}]</span> '
                            f'{n.get("name", "?")}',
                            unsafe_allow_html=True)
            else:
                st.warning(f"No nodes found for '{center_node}'. Check the name and try again.")

        except Exception as e:
            st.error(f"Graph exploration failed: {e}")
            st.info("Ensure Memgraph is running and data is loaded.")

# ═══════════════════════════════════════════════════
# Path Finder
# ═══════════════════════════════════════════════════

st.markdown("---")

st.markdown("""
<h4 style="background: linear-gradient(135deg, #00D4FF, #7B68EE);
           -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">
    🔍 Path Finder
</h4>
""", unsafe_allow_html=True)
st.markdown('<p style="color: #7EB8D8; font-size: 0.85rem;">Find the shortest supply chain path between any two nodes.</p>', unsafe_allow_html=True)

pcol1, pcol2 = st.columns(2)
with pcol1:
    path_start = st.text_input("From", value="Gallium")
with pcol2:
    path_end = st.text_input("To", value="iPhone 16 Pro")

if st.button("Find Shortest Path", use_container_width=True):
    try:
        from graph.algorithms import find_shortest_path
        from dashboard.components.graph_viz import NODE_COLORS

        result = find_shortest_path(path_start, path_end)

        if result:
            chain = result["supply_chain"]
            types = result["node_types"]

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #003322 0%, #004433 100%);
                        border: 1px solid rgba(0, 255, 136, 0.2); border-radius: 14px;
                        padding: 1rem 1.5rem; margin: 1rem 0;
                        box-shadow: 0 0 20px rgba(0, 255, 136, 0.05);">
                <span style="color: #00FF88; font-weight: 700;">✅ Path found — {result['hops']} hops</span>
            </div>
            """, unsafe_allow_html=True)

            # Path visualization
            path_parts = []
            for i, (node, ntype) in enumerate(zip(chain, types)):
                color = NODE_COLORS.get(ntype, "#7EB8D8")
                path_parts.append(
                    f'<span style="background: linear-gradient(135deg, {color}22, {color}0A); color: {color}; '
                    f'padding: 6px 14px; border-radius: 10px; font-weight: 600; '
                    f'border: 1px solid {color}22;">{node}</span>'
                )
                if i < len(chain) - 1:
                    path_parts.append('<span style="color: #4A6A85; margin: 0 6px; font-size: 1.2rem;">→</span>')

            st.markdown(
                f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px; '
                f'padding: 1rem 0;">{"".join(path_parts)}</div>',
                unsafe_allow_html=True)
        else:
            st.warning(f"No path found between {path_start} and {path_end}")

    except Exception as e:
        st.error(f"Path finding failed: {e}")
