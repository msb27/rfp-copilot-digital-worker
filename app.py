# app.py
import streamlit as st
import json
from datetime import datetime
from agent import run_with_audit
from tools.extract import extract_requirements
import PyPDF2
import io

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Pharma RFP Co-Pilot",
    page_icon="rocket",
    layout="centered"
)

# === CUSTOM CSS (causaLens vibe) ===
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #fafafa; }
    .stApp { background-color: #0e1117; }
    .metric-card {
        background-color: #1e1e2e;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #333;
    }
    .tool-call {
        background-color: #272730;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.3rem 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
    .source-tag {
        background-color: #4a5568;
        color: #fff;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# === SIDEBAR: Branding ===
with st.sidebar:
    st.image("https://causalens.com/wp-content/themes/causalens/assets/images/causalens-logo-white.svg", width=200)
    st.markdown("### Digital Worker Demo")
    st.markdown("*Autonomous RFP Response Generator*")
    st.markdown("---")
    st.caption("Built with LangChain • ReAct • RAG • Streamlit")

# === MAIN TITLE ===
st.title("Pharma RFP Co-Pilot")
st.markdown("**Upload an RFP → Get a compliant, winning draft in <60 seconds**")

# === FILE UPLOAD ===
uploaded_file = st.file_uploader(
    "Upload RFP (PDF or TXT)",
    type=["pdf", "txt"],
    help="Supports multi-page PDFs and raw text"
)


def extract_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    else:
        return str(file.read(), "utf-8")


# === MAIN LOGIC ===
if uploaded_file:
    rfp_text = extract_text(uploaded_file)

    with st.spinner("Digital Worker is thinking..."):
        # Create placeholders
        trace_placeholder = st.empty()
        draft_placeholder = st.empty()
        audit_placeholder = st.empty()

        # Run agent with streaming trace
        output, audit = run_with_audit(rfp_text, trace_placeholder, draft_placeholder)

        # === LIVE REASONING TRACE ===
        with trace_placeholder.container():
            st.subheader("Live Reasoning (ReAct)")
            if "intermediate_steps" in st.session_state:
                for i, step in enumerate(st.session_state.intermediate_steps):
                    action = step[0]
                    obs = step[1]
                    with st.expander(f"Step {i + 1}: {action.tool}", expanded=True):
                        st.markdown(f"**Thought:** {action.tool_input}")
                        st.markdown(f"**Observation:** `{obs[:200]}...`")

        # === FINAL DRAFT ===
        with draft_placeholder.container():
            st.subheader("Generated RFP Response")
            st.markdown(output)
            st.download_button(
                "Download Draft (.md)",
                output,
                file_name=f"RFP_Response_{audit['rfp_id']}.md",
                mime="text/markdown"
            )

        # === AUDIT PANEL ===
        with audit_placeholder.container():
            st.subheader("Audit Trail")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration", f"{audit['duration_seconds']:.1f}s")
            with col2:
                st.metric("Tools Used", len(audit['tool_calls']))
            with col3:
                st.metric("Sources Cited", len(audit['sources_cited']))

            st.markdown("**Tool Sequence:**")
            for tool in audit['tool_calls']:
                st.markdown(f"<div class='tool-call'>→ {tool}</div>", unsafe_allow_html=True)

            st.markdown("**Knowledge Sources:**")
            for src in audit['sources_cited']:
                st.markdown(f"<span class='source-tag'>{src}</span>", unsafe_allow_html=True)

            st.markdown("**Full Audit Log:**")
            with st.expander("View JSON"):
                st.json(audit)

            st.button("Route to Review", type="primary")

else:
    st.info("Upload an RFP to activate the Digital Worker.")
    st.markdown("""
    ### How It Works
    1. **Extract** structured requirements
    2. **Search** past wins + compliance
    3. **Generate** compliant draft
    4. **Audit** every step
    """)