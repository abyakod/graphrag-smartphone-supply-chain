"""
PhoneGraph Dashboard — Main Entry Point

Premium deep-blue dashboard for smartphone supply chain intelligence.
Designed for article screenshots with stunning visual appeal.
"""

import sys
sys.path.insert(0, ".")

import streamlit as st

st.set_page_config(
    page_title="PhoneGraph — Supply Chain Intelligence",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════
# Global CSS — Deep Blue Premium Theme
# ═══════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Base Theme ── */
    html, body, .main, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0A1628 0%, #0F2040 40%, #0A1628 100%) !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #060D1A 0%, #0C1A30 50%, #0A1628 100%) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.1) !important;
    }

    [data-testid="stSidebar"] .stMarkdown h1 {
        background: linear-gradient(135deg, #00D4FF, #7B68EE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* ── Metric Cards ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0D1F3C 0%, #152A4A 100%) !important;
        padding: 1rem 1.25rem !important;
        border-radius: 14px !important;
        border: 1px solid rgba(0, 212, 255, 0.12) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.03) !important;
    }

    [data-testid="stMetric"] label {
        color: #7EB8D8 !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.08em !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #00D4FF !important;
        font-weight: 700 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #0066CC 0%, #0088FF 50%, #00AAFF 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 136, 255, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(0, 136, 255, 0.5) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(13, 31, 60, 0.5);
        border-radius: 12px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 8px 20px !important;
        color: #7EB8D8 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066CC, #0088FF) !important;
        color: white !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: rgba(13, 31, 60, 0.5) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 212, 255, 0.08) !important;
    }

    /* ── Text Inputs & Selects ── */
    .stTextInput > div > div > input, .stSelectbox > div > div {
        background: rgba(13, 31, 60, 0.6) !important;
        border: 1px solid rgba(0, 212, 255, 0.15) !important;
        border-radius: 10px !important;
        color: #E2E8F0 !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #00D4FF !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.15) !important;
    }

    /* ── Slider ── */
    .stSlider [data-testid="stThumbValue"] {
        color: #00D4FF !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(0, 212, 255, 0.1) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0A1628; }
    ::-webkit-scrollbar-thumb { background: #1A3050; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #00D4FF; }

    /* ── Hide defaults ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════

with st.sidebar:
    st.markdown("# 📱 PhoneGraph")
    st.markdown("""
<div style="color: #7EB8D8; font-size: 0.85rem; line-height: 1.6; margin-bottom: 1.5rem;">
    Supply Chain Intelligence Engine<br>
    <span style="color: #4A6A85;">Powered by GraphRAG + Memgraph</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="background: linear-gradient(135deg, #0D1F3C, #152A4A); border-radius: 12px;
            padding: 1rem; border: 1px solid rgba(0, 212, 255, 0.08); margin-bottom: 1rem;">
    <div style="color: #4A6A85; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">
        Navigation
    </div>
    <div style="color: #7EB8D8; font-size: 0.85rem; line-height: 2;">
        🔍 Query Engine<br>
        ⚡ Shock Simulator<br>
        📊 Insights & Algorithms<br>
        🕸️ Graph Explorer
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div style="color: #4A6A85; font-size: 0.75rem; line-height: 1.6;">
    🧠 LLM: Ollama / Llama 3<br>
    💾 DB: Memgraph<br>
    📊 7 Node Types · 10 Relations
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Hero Section
# ═══════════════════════════════════════════════════

# ── Hero Section Styles ──
st.markdown("""
<style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section Content ──
st.markdown("""
<div style="text-align: center; padding: 2.5rem 1rem 1.5rem; position: relative;">
<!-- Animated accent line -->
<div style="width: 120px; height: 3px; margin: 0 auto 1.5rem;
            background: linear-gradient(90deg, #00D4FF, #7B68EE, #FF6B9D, #FFD93D, #00D4FF);
            background-size: 300% 100%;
            animation: gradientShift 4s ease infinite;
            border-radius: 2px;"></div>

<!-- Pill badge -->
<div style="margin-bottom: 1.5rem;">
    <span style="background: linear-gradient(135deg, #00D4FF 0%, #7B68EE 100%); color: #FFFFFF;
                 padding: 8px 24px; border-radius: 24px; font-size: 0.9rem; font-weight: 800;
                 letter-spacing: 0.05em; text-transform: uppercase;
                 box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
                 border: 1px solid rgba(255, 255, 255, 0.2);
                 display: inline-block;">
        <span style="animation: pulse 1.5s ease infinite; display: inline-block;">●</span>
        &nbsp;Knowledge Graph + GraphRAG Engine
    </span>
</div>

<!-- Main headline -->
<h1 style="font-size: 3.5rem; font-weight: 800; letter-spacing: -0.04em; margin: 0 0 0.75rem;
           line-height: 1.1;">
    <span style="background: linear-gradient(135deg, #E2E8F0 0%, #FFFFFF 100%);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Smartphone Supply Chain
    </span><br>
    <span style="background: linear-gradient(135deg, #00D4FF 0%, #7B68EE 40%, #FF6B9D 100%);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Intelligence
    </span>
</h1>

<!-- Subtitle -->
<p style="color: #7EB8D8; font-size: 1.25rem; margin: 1rem auto 1.5rem; max-width: 700px;
          font-weight: 300; line-height: 1.6;">
    Ask a question. The AI traverses a <strong style="color: #00D4FF; font-size: 1.4rem; font-weight: 800; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);">knowledge graph</strong> of
    84 nodes and 224 relationships to find answers that
    <strong style="color: #FF6B9D; font-size: 1.4rem; font-weight: 800; text-shadow: 0 0 10px rgba(255, 107, 157, 0.3);">text search can't.</strong>
</p>

<!-- Tech stack pills -->
<div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 0.5rem;">
    <span style="background: rgba(0, 212, 255, 0.08); color: #00D4FF;
                 padding: 5px 14px; border-radius: 8px; font-size: 0.78rem; font-weight: 500;
                 border: 1px solid rgba(0, 212, 255, 0.12);">🧠 GraphRAG</span>
    <span style="background: rgba(123, 104, 238, 0.08); color: #7B68EE;
                 padding: 5px 14px; border-radius: 8px; font-size: 0.78rem; font-weight: 500;
                 border: 1px solid rgba(123, 104, 238, 0.12);">💾 Memgraph</span>
    <span style="background: rgba(255, 107, 157, 0.08); color: #FF6B9D;
                 padding: 5px 14px; border-radius: 8px; font-size: 0.78rem; font-weight: 500;
                 border: 1px solid rgba(255, 107, 157, 0.12);">🦙 Llama 3</span>
    <span style="background: rgba(0, 255, 136, 0.08); color: #00FF88;
                 padding: 5px 14px; border-radius: 8px; font-size: 0.78rem; font-weight: 500;
                 border: 1px solid rgba(0, 255, 136, 0.12);">⚡ LangChain</span>
</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# Connection Status
# ═══════════════════════════════════════════════════

try:
    from graph.connection import get_connection
    conn = get_connection()
    nodes = list(conn.execute_and_fetch("MATCH (n) RETURN count(n) AS cnt"))[0]["cnt"]
    rels = list(conn.execute_and_fetch("MATCH ()-[r]->() RETURN count(r) AS cnt"))[0]["cnt"]
    connected = True
except Exception:
    nodes, rels, connected = 0, 0, False

if connected:
    st.markdown(f"""
    <div style="text-align: center; margin: 0.75rem 0 1.5rem;">
        <span style="background: linear-gradient(135deg, #00442D, #006644); color: #00FF88;
                     padding: 6px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;
                     border: 1px solid rgba(0, 255, 136, 0.2);
                     box-shadow: 0 0 15px rgba(0, 255, 136, 0.1);">
            ● Connected to Memgraph — {nodes} nodes · {rels} relationships
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align: center; margin: 0.75rem 0 1.5rem;">
        <span style="background: rgba(255, 60, 60, 0.15); color: #FF6B6B;
                     padding: 6px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;
                     border: 1px solid rgba(255, 60, 60, 0.2);">
            ○ Memgraph not connected — run: make start && make ingest
        </span>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Stats Cards
# ═══════════════════════════════════════════════════

if connected:
    try:
        node_types = list(conn.execute_and_fetch(
            "MATCH (n) RETURN DISTINCT labels(n)[0] AS type, count(n) AS cnt ORDER BY cnt DESC"
        ))
    except Exception:
        node_types = []

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Nodes", nodes)
    with c2:
        st.metric("Relationships", rels)
    with c3:
        st.metric("Node Types", len(node_types))
    with c4:
        st.metric("Density", f"{rels / max(nodes, 1):.1f}x")

    st.markdown("<br>", unsafe_allow_html=True)

    # Node type breakdown
    col1, col2 = st.columns(2)

    type_colors = {
        "Material": "#FF6B9D", "Company": "#7B68EE", "Component": "#00D4FF",
        "Device": "#FFD93D", "Country": "#00FF88", "RiskEvent": "#FF8C42",
        "Regulation": "#B388FF",
    }

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0D1F3C, #152A4A); border-radius: 14px;
                    padding: 1.5rem; border: 1px solid rgba(0, 212, 255, 0.08);
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
            <div style="color: #4A6A85; font-size: 0.72rem; text-transform: uppercase;
                        letter-spacing: 0.08em; margin-bottom: 1rem;">Graph Composition</div>
        """, unsafe_allow_html=True)

        for nt in node_types:
            color = type_colors.get(nt["type"], "#7EB8D8")
            pct = (nt["cnt"] / max(nodes, 1)) * 100
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="color: {color}; font-size: 0.85rem; width: 100px; font-weight: 500;">
                    ● {nt["type"]}
                </span>
                <div style="flex: 1; height: 8px; background: rgba(0, 212, 255, 0.06);
                            border-radius: 4px; overflow: hidden;">
                    <div style="width: {pct}%; height: 100%; background: linear-gradient(90deg, {color}BB, {color});
                                border-radius: 4px;"></div>
                </div>
                <span style="color: #7EB8D8; font-size: 0.8rem; font-weight: 600; width: 30px; text-align: right;">
                    {nt["cnt"]}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0D1F3C, #152A4A); border-radius: 14px;
                    padding: 1.5rem; border: 1px solid rgba(0, 212, 255, 0.08);
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
            <div style="color: #4A6A85; font-size: 0.72rem; text-transform: uppercase;
                        letter-spacing: 0.08em; margin-bottom: 1rem;">What You Can Do</div>
        """, unsafe_allow_html=True)

        features = [
            ("🔍", "Query Engine", "Ask natural language questions — Llama 3 generates Cypher", "#00D4FF"),
            ("⚡", "Shock Simulator", "Disrupt any node, watch the cascade unfold", "#FF8C42"),
            ("📊", "Graph Insights", "PageRank, Betweenness, Community Detection", "#7B68EE"),
            ("🕸️", "Graph Explorer", "Interactive Pyvis visualization + path finder", "#00FF88"),
        ]

        for icon, title, desc, color in features:
            st.markdown(f"""
            <div style="display: flex; gap: 12px; padding: 10px 0;
                        border-bottom: 1px solid rgba(0, 212, 255, 0.05);">
                <span style="font-size: 1.4rem; width: 30px;">{icon}</span>
                <div>
                    <div style="color: #E2E8F0; font-weight: 600; font-size: 0.9rem;">{title}</div>
                    <div style="color: #4A6A85; font-size: 0.8rem;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Supply Chain Path Demo
# ═══════════════════════════════════════════════════

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #0D1F3C 0%, #1A2D4A 50%, #0D1F3C 100%);
            border-radius: 16px; padding: 2rem; text-align: center;
            border: 1px solid rgba(0, 212, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
    <div style="color: #4A6A85; font-size: 0.72rem; text-transform: uppercase;
                letter-spacing: 0.1em; margin-bottom: 1rem;">
        Example Supply Chain Traversal
    </div>
    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap;">
        <span style="background: linear-gradient(135deg, #FF6B9D33, #FF6B9D11); color: #FF6B9D;
                     padding: 8px 16px; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
                     border: 1px solid #FF6B9D33;">Gallium</span>
        <span style="color: #4A6A85; font-size: 1.2rem;">→</span>
        <span style="background: linear-gradient(135deg, #00FF8833, #00FF8811); color: #00FF88;
                     padding: 8px 16px; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
                     border: 1px solid #00FF8833;">China</span>
        <span style="color: #4A6A85; font-size: 1.2rem;">→</span>
        <span style="background: linear-gradient(135deg, #00D4FF33, #00D4FF11); color: #00D4FF;
                     padding: 8px 16px; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
                     border: 1px solid #00D4FF33;">A17 Pro Chip</span>
        <span style="color: #4A6A85; font-size: 1.2rem;">→</span>
        <span style="background: linear-gradient(135deg, #FFD93D33, #FFD93D11); color: #FFD93D;
                     padding: 8px 16px; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
                     border: 1px solid #FFD93D33;">iPhone 16 Pro</span>
        <span style="color: #4A6A85; font-size: 1.2rem;">→</span>
        <span style="background: linear-gradient(135deg, #FF8C4233, #FF8C4211); color: #FF8C42;
                     padding: 8px 16px; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
                     border: 1px solid #FF8C4233;">+$85 (+7.1%)</span>
    </div>
    <div style="color: #4A6A85; font-size: 0.8rem; margin-top: 1rem;">
        4 hops · 5 nodes traversed · This is what GraphRAG does that text RAG can't
    </div>
</div>
""", unsafe_allow_html=True)
