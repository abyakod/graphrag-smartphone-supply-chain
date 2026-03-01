"""
PhoneGraph: Query Engine Page — Blue Premium Theme + Live Thought Process

Natural language Q&A with GraphRAG vs Vanilla RAG comparison.
Shows the LLM's thinking process step-by-step so users never stare at a blank spinner.
"""

import sys
sys.path.insert(0, ".")

import streamlit as st
import time

st.set_page_config(page_title="Query Engine — PhoneGraph", page_icon="🔍", layout="wide")

# ═══════════════════════════════════════════════════
# Page Header
# ═══════════════════════════════════════════════════

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem;
               background: linear-gradient(135deg, #00D4FF, #7B68EE);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🔍 Query Engine
    </h1>
    <p style="color: #4A6A85; font-size: 0.95rem; margin: 0;">
        Ask any question about the smartphone supply chain. Watch the AI think in real-time.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# Example Questions
# ═══════════════════════════════════════════════════

EXAMPLE_QUESTIONS = [
    "What happens to iPhone prices if China bans Gallium exports?",
    "Which company is the single biggest chokepoint in the supply chain?",
    "If TSMC shuts down, which devices are affected and by how much?",
    "What is the shortest path from Cobalt to Samsung Galaxy?",
    "What materials are needed to make smartphone chips?",
    "Which countries have the highest geopolitical risk?",
]

# Mode selection
col1, col2 = st.columns([3, 1])

with col1:
    question = st.text_input(
        "Your question",
        placeholder="e.g., What happens if China bans Gallium exports?",
        label_visibility="collapsed",
    )

with col2:
    mode = st.selectbox("Mode", ["⚔️ Compare Both", "🧠 GraphRAG", "📄 Vanilla RAG"])

# Example buttons
st.markdown('<p style="color: #4A6A85; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">Try these questions</p>', unsafe_allow_html=True)
example_cols = st.columns(3)
for i, q in enumerate(EXAMPLE_QUESTIONS):
    with example_cols[i % 3]:
        if st.button(q[:50] + "…" if len(q) > 50 else q, key=f"ex_{i}", use_container_width=True):
            question = q
            st.session_state["question"] = q

# ═══════════════════════════════════════════════════
# Phase icons for the thought process
# ═══════════════════════════════════════════════════

PHASE_ICONS = {
    "init": "🔌",
    "cypher": "⚡",
    "execute": "💾",
    "synthesize": "🧠",
    "done": "✅",
    "graphrag_start": "🧠",
    "graphrag_init": "🔌",
    "graphrag_cypher": "⚡",
    "graphrag_execute": "💾",
    "graphrag_synthesize": "🧠",
    "graphrag_done": "✅",
    "vanilla_start": "📄",
    "vanilla_done": "📄",
    "compare_done": "🏆",
}

PHASE_LABELS = {
    "init": "Initializing LLM",
    "cypher": "Generating Cypher Query",
    "execute": "Querying Knowledge Graph",
    "synthesize": "Synthesizing Answer",
    "done": "Complete",
    "graphrag_start": "GraphRAG Pipeline",
    "graphrag_init": "Connecting to LLM",
    "graphrag_cypher": "Generating Cypher Query",
    "graphrag_execute": "Traversing Knowledge Graph",
    "graphrag_synthesize": "Synthesizing Answer",
    "graphrag_done": "GraphRAG Complete",
    "vanilla_start": "Vanilla RAG Pipeline",
    "vanilla_done": "Vanilla RAG Complete",
    "compare_done": "Comparison Complete",
}

# ═══════════════════════════════════════════════════
# Execute Query with Live Thought Process
# ═══════════════════════════════════════════════════

if question:
    try:
        from graphrag.chain import get_rag
        rag = get_rag()

        if "Compare" in mode:
            # ── Compare Both with live status ──
            with st.status("🧠 **AI is thinking…**", expanded=True) as status:
                result = None
                for phase, detail, partial in rag.compare_step_by_step(question):
                    icon = PHASE_ICONS.get(phase, "⏳")
                    label = PHASE_LABELS.get(phase, phase)
                    st.write(f"{icon} **{label}** — {detail}")
                    if phase == "compare_done":
                        result = partial
                status.update(label="✅ **Query complete!**", state="complete", expanded=False)

            if result:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("""
<div style="background: linear-gradient(135deg, #0D1F3C 0%, #152A4A 100%);
            border: 1px solid rgba(0, 212, 255, 0.12);
            border-top: 3px solid #00D4FF;
            border-radius: 14px; padding: 1.5rem; margin-top: 0.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
        <span style="font-size: 1.3rem;">🧠</span>
        <span style="color: #E2E8F0; font-weight: 700; font-size: 1.05rem;">GraphRAG</span>
        <span style="background: linear-gradient(135deg, #00D4FF33, #00D4FF11); color: #00D4FF;
                     padding: 3px 10px; border-radius: 12px; font-size: 0.68rem; font-weight: 600;
                     border: 1px solid #00D4FF33;">GRAPH TRAVERSAL</span>
    </div>
</div>
""", unsafe_allow_html=True)
                    st.markdown(result.get('graphrag_answer', 'N/A'))

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Nodes", result.get("graphrag_nodes", 0))
                    with m2:
                        st.metric("Hops", result.get("graphrag_hops", 0))
                    with m3:
                        st.metric("Confidence", f"{result.get('graphrag_confidence', 0):.0%}")

                    # Show Cypher query
                    cypher = result.get("graphrag_cypher", "")
                    if cypher:
                        with st.expander("🔧 Generated Cypher Query"):
                            st.code(cypher, language="cypher")

                    # Show reasoning chain
                    reasoning = result.get("graphrag_reasoning", [])
                    if reasoning:
                        with st.expander("📋 Reasoning Chain"):
                            for step in reasoning:
                                st.markdown(f"- {step}")

                with col2:
                    st.markdown("""
<div style="background: linear-gradient(135deg, #0D1F3C 0%, #152A4A 100%);
            border: 1px solid rgba(0, 212, 255, 0.08);
            border-top: 3px solid #4A6A85;
            border-radius: 14px; padding: 1.5rem; margin-top: 0.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
        <span style="font-size: 1.3rem;">📄</span>
        <span style="color: #E2E8F0; font-weight: 700; font-size: 1.05rem;">Vanilla RAG</span>
        <span style="background: rgba(74, 106, 133, 0.2); color: #4A6A85;
                     padding: 3px 10px; border-radius: 12px; font-size: 0.68rem; font-weight: 600;
                     border: 1px solid rgba(74, 106, 133, 0.3);">TEXT ONLY</span>
    </div>
</div>
""", unsafe_allow_html=True)
                    st.markdown(result.get('vanilla_rag_answer', 'N/A'))

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Matches", result.get("vanilla_rag_nodes", 0))
                    with m2:
                        st.metric("Documents", result.get("vanilla_rag_docs", result.get("vanilla_rag_nodes", 0)))
                    with m3:
                        st.metric("Confidence", f"{result.get('vanilla_rag_confidence', 0):.0%}")

                # Winner banner
                why = result.get("why_graphrag_wins", "")
                st.markdown(f"""
<div style="background: linear-gradient(135deg, #002844 0%, #003366 100%);
            border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 14px;
            padding: 1.25rem 1.5rem; margin-top: 1rem;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.08);
            display: flex; align-items: center; gap: 12px;">
    <span style="font-size: 2rem;">🏆</span>
    <div>
        <div style="background: linear-gradient(135deg, #00D4FF, #7B68EE);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    font-weight: 700; font-size: 1.05rem;">Winner: GraphRAG</div>
        <div style="color: #7EB8D8; font-size: 0.85rem; margin-top: 4px;">{why}</div>
    </div>
</div>
""", unsafe_allow_html=True)

        elif "Vanilla" in mode:
            # ── Vanilla RAG ──
            with st.status("📄 **Running Vanilla RAG…**", expanded=True) as status:
                st.write("📄 **Text Search** — Scanning node descriptions…")
                result = rag.vanilla_rag_query(question)
                st.write(f"✅ Found {result.get('nodes_found', 0)} text matches")
                status.update(label="✅ **Complete**", state="complete", expanded=False)

            st.markdown("#### 📄 Vanilla RAG Answer")
            st.markdown(result.get("answer", "No answer"))
            st.caption(f"Nodes found: {result.get('nodes_found', 0)} · "
                      f"Confidence: {result.get('confidence', 0):.0%}")

        else:
            # ── GraphRAG with live thought process ──
            with st.status("🧠 **AI is thinking…**", expanded=True) as status:
                result = None
                for phase, detail, partial in rag.query_step_by_step(question):
                    icon = PHASE_ICONS.get(phase, "⏳")
                    label = PHASE_LABELS.get(phase, phase)
                    st.write(f"{icon} **{label}** — {detail}")
                    if phase == "done":
                        result = partial
                status.update(label="✅ **Query complete!**", state="complete", expanded=False)

            if result:
                st.markdown("#### 🧠 GraphRAG Answer")
                st.markdown(result.get("answer", "No answer"))

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Nodes Traversed", result.get("nodes_traversed", 0))
                with m2:
                    st.metric("Graph Hops", result.get("hops", 0))
                with m3:
                    st.metric("Confidence", f"{result.get('confidence', 0):.0%}")

                cypher = result.get("cypher_query", "")
                if cypher and cypher != "N/A (hybrid retrieval mode)":
                    with st.expander("🔧 Generated Cypher Query"):
                        st.code(cypher, language="cypher")

                if result.get("reasoning_chain"):
                    with st.expander("📋 Reasoning Chain"):
                        for step in result["reasoning_chain"]:
                            st.markdown(f"- {step}")

    except Exception as e:
        st.error(f"Query failed: {e}")
        st.info("💡 Ensure Memgraph is running (`make start`) and Ollama is serving (`ollama serve`).")
