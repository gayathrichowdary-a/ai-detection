import streamlit as st
import base64
import os

def get_robot_image_b64():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    image_paths = [
        os.path.join(root_dir, "assets", "dashboard_robot.png"),
        os.path.join(root_dir, "assets", "dashboard_robot.jpg"),
        os.path.join(base_dir, "assets", "dashboard_robot.png"),
        "assets/dashboard_robot.png",
    ]
    for p in image_paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return None

def home_page():
    # Robot Image Tag
    img_b64 = get_robot_image_b64()
    img_tag = f'<img src="data:image/png;base64,{img_b64}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 20px; box-shadow: 0 12px 28px rgba(2, 18, 53, 0.45); border: 1.5px solid rgba(255, 255, 255, 0.2);" alt="Dashboard AI Robot" />' if img_b64 else '<div style="font-size: 72px;">🤖</div>'

    user_name = st.session_state.get("username") or st.session_state.get("user", {}).get("name") or "Siri"

    # Hero Banner matching video
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
                    border-radius: 20px; padding: 26px 30px;
                    border: 1px solid #dbeafe; display: flex; align-items: center;
                    justify-content: space-between; margin-bottom: 24px; gap: 24px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 280px;">
                <div style="font-size: 13px; color: #64748b; margin-bottom: 6px; font-weight: 500;">
                    Next-Generation Knowledge Intelligence with Graph RAG & ARES Quality Verification
                </div>
                <h1 style="color: #0f172a; font-size: 30px; font-weight: 800; margin: 0 0 10px 0;">
                    Welcome back, {user_name}! 👋
                </h1>
                <p style="color: #475569; font-size: 15px; margin: 0; line-height: 1.5; max-width: 650px;">
                    Your adaptive multi-agent knowledge mesh is fully operational. Ready to ingest documents, traverse knowledge subgraphs, and verify grounded reasoning.
                </p>
            </div>
            <div style="flex-shrink: 0; display: flex; justify-content: center; align-items: center;">
                {img_tag}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 4 Top Metrics matching video frame 00:47
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                <div style="font-size: 28px; font-weight: 800; color: #2563eb;">6</div>
                <div style="font-size: 11px; font-weight: 800; color: #0f172a; letter-spacing: 0.5px; text-transform: uppercase;">ACTIVE DOCUMENTS</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                <div style="font-size: 28px; font-weight: 800; color: #2563eb;">8</div>
                <div style="font-size: 11px; font-weight: 800; color: #0f172a; letter-spacing: 0.5px; text-transform: uppercase;">NODES LANGGRAPH PIPELINE</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                <div style="font-size: 28px; font-weight: 800; color: #2563eb;">85.8%</div>
                <div style="font-size: 11px; font-weight: 800; color: #0f172a; letter-spacing: 0.5px; text-transform: uppercase;">AVG SOURCE TRUST</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                <div style="font-size: 28px; font-weight: 800; color: #2563eb;">95% CI</div>
                <div style="font-size: 11px; font-weight: 800; color: #0f172a; letter-spacing: 0.5px; text-transform: uppercase;">ARES PPI BOUNDS</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Multi-Agent Orchestration Architecture (LangGraph)
    st.markdown("### 🔀 Multi-Agent Orchestration Architecture (LangGraph)")
    st.caption("Live execution pipeline: State transitions from query intent to hybrid grounding and ARES verification.")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 🧩 Core Architectural Pillars")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 8px;">
                    ⚡ Hybrid Retrieval
                </div>
                <p style="color: #64748b; font-size: 14px; line-height: 1.6; margin: 0;">
                    Structured entity relations (Graph RAG), Dynamic dense vector search (FAISS) with structured entity relations (Graph RAG). Dynamic source reliability multipliers prioritize official Tier 1 policies over informal working notes.
                </p>
            </div>
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 8px;">
                    🎯 ARES Quality Evaluation
                </div>
                <p style="color: #64748b; font-size: 14px; line-height: 1.6; margin: 0;">
                    Implements Stanford's ARES benchmark with Prediction-Powered Inference (PPI). Automatically validates context relevance, grounded faithfulness, and answer alignment with 95% confidence intervals.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 8px;">
                    🧠 Memory System
                </div>
                <p style="color: #64748b; font-size: 14px; line-height: 1.6; margin: 0;">
                    Episodic conversation memory retains session context while persistent profile memory stores role-based user preferences, departments, and compliance rules across restarts.
                </p>
            </div>
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 8px;">
                    ⚖️ Multi-Doc Comparison & Conflict Resolution
                </div>
                <p style="color: #64748b; font-size: 14px; line-height: 1.6; margin: 0;">
                    Cross-analyzes multiple uploaded documents side-by-side. Highlights discrepancies, extracts overlapping clauses, and resolves ambiguities using authority tier precedence rules.
                </p>
            </div>
        """, unsafe_allow_html=True)

render_home = home_page
__all__ = ["home_page", "render_home"]