"""
PhoneGraph: Shock Simulator Page — Blue Premium Theme

Simulate supply chain disruptions and see cascading price impacts.
"""

import sys
sys.path.insert(0, ".")

import streamlit as st

st.set_page_config(page_title="Shock Simulator — PhoneGraph", page_icon="⚡", layout="wide")

# ═══════════════════════════════════════════════════
# Page Header
# ═══════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem;
               background: linear-gradient(135deg, #FF8C42, #FFD93D);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        ⚡ Shock Simulator
    </h1>
    <p style="color: #4A6A85; font-size: 0.95rem; margin: 0;">
        Disrupt any node in the supply chain. Watch the cascade unfold across devices, components, and prices.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Input Controls
# ═══════════════════════════════════════════════════

col1, col2, col3 = st.columns(3)

with col1:
    node_type = st.selectbox("Disruption type", ["Material", "Company", "Country"])

DISRUPTION_OPTIONS = {
    "Material": ["Gallium", "Neon", "Cobalt", "Rare Earth Elements", "Lithium", "Indium", "Germanium"],
    "Company": ["TSMC", "ASML", "Samsung", "Apple", "Qualcomm", "SK Hynix", "Micron", "Foxconn", "Corning", "Murata"],
    "Country": ["China", "Taiwan", "South Korea", "Japan", "USA", "DRC", "Ukraine", "Netherlands"],
}

with col2:
    disrupted_node = st.selectbox("Target", DISRUPTION_OPTIONS.get(node_type, []))

with col3:
    severity = st.slider("Severity", 1, 10, 8, help="1 = minor disruption, 10 = total shutdown")

# Scenario context
scenarios = {
    ("Material", "Gallium"): ("🇨🇳", "China Gallium export ban — mirrors the Aug 2023 restrictions", "#FF6B6B"),
    ("Material", "Neon"): ("🇺🇦", "Ukraine conflict cuts Neon supply — 67% of global production", "#FF8C42"),
    ("Material", "Cobalt"): ("🇨🇩", "DRC mining disruption or ethical sourcing regulations", "#FF8C42"),
    ("Company", "TSMC"): ("🇹🇼", "TSMC fab shutdown — earthquake or Taiwan Strait crisis", "#FF6B6B"),
    ("Company", "ASML"): ("🇳🇱", "ASML export restrictions — sole EUV lithography maker", "#FF6B6B"),
    ("Country", "China"): ("🌏", "Full China trade embargo scenario", "#FF6B6B"),
    ("Country", "Taiwan"): ("🌏", "Taiwan Strait blockade scenario", "#FF6B6B"),
}

scenario = scenarios.get((node_type, disrupted_node))
if scenario:
    flag, desc, color = scenario
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}15, {color}08); border: 1px solid {color}30;
                border-radius: 12px; padding: 0.85rem 1.25rem; margin: 0.5rem 0;
                box-shadow: 0 0 15px {color}08;">
        <span style="color: {color}; font-weight: 600;">{flag} {desc}</span>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Run Simulation
# ═══════════════════════════════════════════════════

if st.button("⚡ Run Shock Simulation", type="primary", use_container_width=True):
    with st.spinner("Calculating ripple effects across the supply chain…"):
        try:
            from algorithms.risk_scoring import simulate_supply_shock

            result = simulate_supply_shock(
                disrupted_node=disrupted_node,
                node_type=node_type,
                severity=severity,
            )

            st.markdown("---")

            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Devices Affected", result.get("devices_affected_count", 0))
            with m2:
                st.metric("Total Impact", f"${result.get('total_price_impact_usd', 0):,.0f}")
            with m3:
                st.metric("Most Vulnerable", result.get("most_vulnerable", "N/A"))
            with m4:
                st.metric("Recovery", f"{result.get('recovery_estimate_months', 0)} months")

            # Device impact cards
            st.markdown("#### Affected Devices")
            devices = result.get("affected_devices", [])

            if devices:
                for device in devices:
                    is_single = device.get("single_source_risk", False)
                    risk_color = "#FF6B6B" if is_single else "#FF8C42"
                    badge = f'<span style="background:{risk_color}18;color:{risk_color};padding:3px 10px;border-radius:12px;font-size:0.68rem;font-weight:600;border:1px solid {risk_color}33;margin-left:8px;">SINGLE-SOURCE</span>' if is_single else ""

                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #0D1F3C 0%, #152A4A 100%);
                                border: 1px solid rgba(0, 212, 255, 0.08); border-radius: 14px;
                                padding: 1.25rem; margin-bottom: 0.5rem;
                                display: flex; justify-content: space-between; align-items: center;
                                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);">
                        <div>
                            <span style="color: #E2E8F0; font-weight: 700;">{device.get('device', 'Unknown')}</span>
                            {badge}
                            <br>
                            <span style="color: #4A6A85; font-size: 0.8rem;">
                                {device.get('brand', '')} · ${device.get('current_price_usd', 0):,.0f}
                            </span>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: {risk_color}; font-size: 1.5rem; font-weight: 800;">
                                +${device.get('price_increase_usd', 0):,.0f}
                            </div>
                            <span style="color: #7EB8D8; font-size: 0.8rem;">
                                +{device.get('price_increase_pct', 0):.1f}%
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No devices directly affected. Try a different disruption target.")

            # Ripple paths
            ripple_paths = result.get("ripple_path", [])
            if ripple_paths:
                with st.expander("🌊 Ripple Effect Paths"):
                    for path in ripple_paths:
                        st.code(path, language="text")

        except Exception as e:
            st.error(f"Simulation failed: {e}")
            st.info("Ensure Memgraph is running and data is loaded.")

# ═══════════════════════════════════════════════════
# Quick Scenarios
# ═══════════════════════════════════════════════════

st.markdown("---")
st.markdown("#### Quick Scenarios")

scol1, scol2, scol3 = st.columns(3)

quick_scenarios = [
    ("🇨🇳 China Gallium Ban",
     "Aug 2023: China restricted Gallium and Germanium exports. What if they fully stop?",
     "#FF6B6B"),
    ("🇹🇼 TSMC Shutdown",
     "TSMC makes 90% of advanced chips. One earthquake could halt all flagship phones.",
     "#FF8C42"),
    ("🇺🇦 Neon Crisis",
     "Ukraine produces 67% of semiconductor-grade Neon. Conflict = chip shortage.",
     "#FFD93D"),
]

for col, (title, desc, color) in zip([scol1, scol2, scol3], quick_scenarios):
    with col:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0D1F3C 0%, #152A4A 100%);
                    border: 1px solid rgba(0, 212, 255, 0.08); border-radius: 14px;
                    padding: 1.5rem; border-top: 3px solid {color};
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
            <div style="color: #E2E8F0; font-weight: 700; margin-bottom: 0.5rem;">{title}</div>
            <div style="color: #7EB8D8; font-size: 0.85rem; line-height: 1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
