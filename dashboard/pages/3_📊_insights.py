"""
PhoneGraph: Insights & Algorithms Page — Blue Premium Theme

Graph algorithm analytics and supply chain insights.
"""

import sys
sys.path.insert(0, ".")

import streamlit as st

st.set_page_config(page_title="Insights — PhoneGraph", page_icon="📊", layout="wide")

# ═══════════════════════════════════════════════════
# Page Header
# ═══════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem;
               background: linear-gradient(135deg, #7B68EE, #B388FF);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        📊 Insights & Algorithms
    </h1>
    <p style="color: #4A6A85; font-size: 0.95rem; margin: 0;">
        Mind-blowing discoveries from running graph algorithms on the smartphone supply chain.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Supply Chain Insights
# ═══════════════════════════════════════════════════

try:
    from api.routes.insights import _compute_insights

    insights = _compute_insights()

    if insights:
        for i in range(0, len(insights), 2):
            col1, col2 = st.columns(2)

            for col, idx in [(col1, i), (col2, i + 1)]:
                if idx < len(insights):
                    insight = insights[idx]
                    sev = insight.get("severity", "info")
                    colors = {"critical": "#FF6B6B", "warning": "#FFD93D", "info": "#00D4FF"}
                    color = colors.get(sev, "#00D4FF")

                    with col:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #0D1F3C 0%, #152A4A 100%);
                                    border: 1px solid rgba(0, 212, 255, 0.08);
                                    border-left: 3px solid {color}; border-radius: 14px;
                                    padding: 1.5rem; margin-bottom: 0.75rem;
                                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
                            <div style="color: {color}; font-weight: 700; font-size: 0.95rem;
                                        margin-bottom: 0.5rem;">
                                {insight["title"]}
                            </div>
                            <div style="color: #7EB8D8; font-size: 0.85rem; line-height: 1.6;
                                        margin-bottom: 1rem;">
                                {insight["description"]}
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <span style="font-size: 2rem; font-weight: 800; color: {color};">
                                    {insight["metric_value"]}
                                </span>
                                <span style="color: #4A6A85; font-size: 0.75rem;">
                                    {insight["metric_label"]}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("No insights available. Load data first with `make ingest`.")

except Exception as e:
    st.warning(f"Could not compute insights: {e}")

# ═══════════════════════════════════════════════════
# Algorithm Results
# ═══════════════════════════════════════════════════

st.markdown("---")
st.markdown("#### Graph Algorithms")

tab1, tab2, tab3 = st.tabs(["👑 PageRank", "🎯 Betweenness", "🏘️ Communities"])

with tab1:
    st.markdown('<p style="color: #7EB8D8; font-size: 0.85rem;">Ranks nodes by influence — how many important nodes depend on them.</p>', unsafe_allow_html=True)
    try:
        from graph.algorithms import run_pagerank
        results = run_pagerank(limit=10)

        if results:
            for i, r in enumerate(results, 1):
                rank_val = r['rank']
                bar_width = min(rank_val * 1000, 100)
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"<span style='color:#4A6A85;font-size:0.8rem;'>#{i}</span>"

                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0;
                            border-bottom: 1px solid rgba(0, 212, 255, 0.06);">
                    <span style="width: 30px; text-align: center; font-size: 0.9rem;">{medal}</span>
                    <span style="color: #E2E8F0; font-weight: 600; width: 140px;">{r['name']}</span>
                    <span style="color: #4A6A85; font-size: 0.8rem; width: 80px;">{r['type']}</span>
                    <div style="flex: 1; height: 8px; background: rgba(0, 212, 255, 0.06);
                                border-radius: 4px; overflow: hidden;">
                        <div style="width: {bar_width}%; height: 100%;
                                    background: linear-gradient(90deg, #7B68EE, #00D4FF);
                                    border-radius: 4px;"></div>
                    </div>
                    <span style="color: #00D4FF; font-weight: 700; font-size: 0.85rem; width: 60px; text-align: right;">
                        {rank_val:.4f}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"PageRank unavailable: {e}")

with tab2:
    st.markdown('<p style="color: #7EB8D8; font-size: 0.85rem;">Finds hidden chokepoints — nodes on the most shortest paths.</p>', unsafe_allow_html=True)
    try:
        from graph.algorithms import run_betweenness_centrality
        results = run_betweenness_centrality(limit=10)

        if results:
            for i, r in enumerate(results, 1):
                bc_val = r['betweenness_centrality']
                bar_width = min(bc_val * 200, 100)
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"<span style='color:#4A6A85;font-size:0.8rem;'>#{i}</span>"

                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0;
                            border-bottom: 1px solid rgba(0, 212, 255, 0.06);">
                    <span style="width: 30px; text-align: center; font-size: 0.9rem;">{medal}</span>
                    <span style="color: #E2E8F0; font-weight: 600; width: 140px;">{r['name']}</span>
                    <span style="color: #4A6A85; font-size: 0.8rem; width: 80px;">{r['type']}</span>
                    <div style="flex: 1; height: 8px; background: rgba(0, 212, 255, 0.06);
                                border-radius: 4px; overflow: hidden;">
                        <div style="width: {bar_width}%; height: 100%;
                                    background: linear-gradient(90deg, #FF8C42, #FFD93D);
                                    border-radius: 4px;"></div>
                    </div>
                    <span style="color: #FFD93D; font-weight: 700; font-size: 0.85rem; width: 60px; text-align: right;">
                        {bc_val:.4f}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Betweenness unavailable: {e}")

with tab3:
    st.markdown('<p style="color: #7EB8D8; font-size: 0.85rem;">Detects natural clusters — which entities form supply chain ecosystems.</p>', unsafe_allow_html=True)
    try:
        from graph.algorithms import run_community_detection
        communities = run_community_detection()

        community_colors = ["#00D4FF", "#00FF88", "#FF8C42", "#FF6B9D", "#FFD93D", "#B388FF"]

        if communities:
            for i, comm in enumerate(communities):
                color = community_colors[i % len(community_colors)]
                with st.expander(f"Community {i + 1} — {comm['size']} members"):
                    members_html = "".join(
                        f'<span style="background: linear-gradient(135deg, {color}22, {color}0A); color: {color}; '
                        f'padding: 5px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 500; '
                        f'margin: 3px; display: inline-block; border: 1px solid {color}22;">'
                        f'{member}</span>'
                        for member in comm["members"]
                    )
                    st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 4px;">{members_html}</div>',
                               unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Community detection unavailable: {e}")
