"""
PhoneGraph: Metric Cards Component

Reusable Streamlit metric display cards with custom styling.
"""

import streamlit as st
from typing import Any, Dict, List, Optional


def render_metric_card(
    title: str,
    value: str,
    description: str = "",
    color: str = "#7c83ff",
    icon: str = "📊",
) -> None:
    """Render a styled metric card."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid {color};
        margin-bottom: 1rem;
    ">
        <div style="font-size: 0.85rem; color: #a0a0ff; margin-bottom: 0.25rem;">
            {icon} {title}
        </div>
        <div style="font-size: 2.5rem; font-weight: bold; color: {color};">
            {value}
        </div>
        <div style="font-size: 0.8rem; color: #888;">
            {description}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_insight_card(
    title: str,
    description: str,
    metric_value: str,
    metric_label: str,
    severity: str = "info",
) -> None:
    """Render an insight card with severity coloring."""
    severity_colors = {
        "critical": "#e94560",
        "warning": "#ffd700",
        "info": "#7c83ff",
    }
    color = severity_colors.get(severity, "#7c83ff")
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid {color};
        margin-bottom: 1rem;
    ">
        <h3 style="color: {color}; margin-bottom: 0.5rem; font-size: 1.1rem;">
            {title}
        </h3>
        <p style="color: #ccc; font-size: 0.95rem; margin-bottom: 1rem;">
            {description}
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 2rem; font-weight: bold; color: {color};">
                {metric_value}
            </span>
            <span style="font-size: 0.8rem; color: #888;">
                {metric_label}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_device_impact_card(device: Dict[str, Any]) -> None:
    """Render a device impact card for shock simulation."""
    risk_color = "#e94560" if device.get("single_source_risk") else "#ffd700"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid {risk_color};
        margin-bottom: 0.75rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong style="color: white; font-size: 1rem;">
                    {device.get('device', 'Unknown')}
                </strong>
                <br>
                <span style="color: #888; font-size: 0.85rem;">
                    {device.get('brand', '')} | Current: ${device.get('current_price_usd', 0):,.0f}
                </span>
            </div>
            <div style="text-align: right;">
                <div style="color: {risk_color}; font-size: 1.5rem; font-weight: bold;">
                    +${device.get('price_increase_usd', 0):,.0f}
                </div>
                <span style="color: #888; font-size: 0.8rem;">
                    +{device.get('price_increase_pct', 0):.1f}%
                </span>
            </div>
        </div>
        {'<div style="color: #e94560; font-size: 0.8rem; margin-top: 0.5rem;">⚠️ SINGLE-SOURCE RISK</div>' if device.get('single_source_risk') else ''}
    </div>
    """, unsafe_allow_html=True)
