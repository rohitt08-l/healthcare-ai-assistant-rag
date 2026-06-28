import json
from typing import Any, Dict, List

import requests
import streamlit as st


# -------------------------------------------------------------------
# Page configuration
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Health Assistant",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# -------------------------------------------------------------------
# Custom CSS — simple, calm, accessible design
# -------------------------------------------------------------------

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ── Page background ── */
        .stApp {
            background-color: #f0f6ff;
        }

        /* ── Hide default Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden; }

        /* ── Top banner ── */
        .top-banner {
            background: linear-gradient(135deg, #1a5fb4 0%, #1c7ed6 100%);
            border-radius: 20px;
            padding: 2rem 2.2rem 1.6rem;
            margin-bottom: 1.8rem;
            color: white;
        }
        .top-banner h1 {
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 0.3rem;
            letter-spacing: -0.5px;
        }
        .top-banner p {
            font-size: 1rem;
            opacity: 0.88;
            margin: 0;
        }

        /* ── Section heading ── */
        .section-label {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1a3a5c;
            margin: 1.6rem 0 0.6rem;
        }

        /* ── Plain cards ── */
        .simple-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            border: 1.5px solid #d6e4f7;
            margin-bottom: 1rem;
        }

        /* ── Status banners ── */
        .ok-banner {
            background: #e6f9ef;
            border-left: 5px solid #2ecc71;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            color: #1a5c35;
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        .err-banner {
            background: #fff0f0;
            border-left: 5px solid #e74c3c;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            color: #7f1d1d;
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        .info-banner {
            background: #eaf3ff;
            border-left: 5px solid #1c7ed6;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            color: #1a3a5c;
            font-size: 1rem;
            margin-bottom: 1rem;
        }

        /* ── Answer box ── */
        .answer-box {
            background: #ffffff;
            border-radius: 16px;
            border: 2px solid #1c7ed6;
            padding: 1.6rem;
            font-size: 1.05rem;
            line-height: 1.7;
            color: #1a3a5c;
            margin-bottom: 1rem;
        }
        .answer-box .tool-tag {
            display: inline-block;
            background: #dbeafe;
            color: #1a5fb4;
            font-weight: 700;
            font-size: 0.8rem;
            border-radius: 999px;
            padding: 0.25rem 0.75rem;
            margin-bottom: 0.8rem;
        }

        /* ── Appointment card ── */
        .appt-card {
            background: #f0fff8;
            border: 1.5px solid #b2f0d4;
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 0.8rem;
        }
        .appt-card h4 { color: #065f46; margin: 0 0 0.4rem; font-size: 1.05rem; }
        .appt-card p  { color: #064e3b; margin: 0.15rem 0; font-size: 0.95rem; }

        /* ── Chunk card ── */
        .chunk-card {
            background: #fafbff;
            border: 1.5px solid #d6e4f7;
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 0.8rem;
            font-size: 0.94rem;
            color: #334155;
        }

        /* ── Step badges (for how-to section) ── */
        .step-row {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .step-badge {
            min-width: 2.4rem;
            height: 2.4rem;
            border-radius: 50%;
            background: #1c7ed6;
            color: white;
            font-weight: 700;
            font-size: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .step-text { padding-top: 0.3rem; font-size: 0.98rem; color: #334155; }

        /* ── Big primary button override ── */
        .stButton > button[kind="primary"] {
            background: #1c7ed6 !important;
            border: none !important;
            border-radius: 12px !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            color: white !important;
            width: 100% !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: #1a5fb4 !important;
        }
        .stButton > button:not([kind="primary"]) {
            border-radius: 10px !important;
            font-size: 0.95rem !important;
        }

        /* ── Text inputs ── */
        .stTextInput input, .stTextArea textarea {
            border-radius: 12px !important;
            border: 1.5px solid #c3d9f5 !important;
            font-size: 1rem !important;
            padding: 0.7rem 1rem !important;
        }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #1a3a5c;
        }

        /* ── Footer ── */
        .footer-note {
            text-align: center;
            color: #94a3b8;
            font-size: 0.82rem;
            padding: 2rem 0 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8000"

if "user_id" not in st.session_state:
    st.session_state.user_id = "user123"


# -------------------------------------------------------------------
# Helper functions (unchanged logic)
# -------------------------------------------------------------------

def get_api_base_url() -> str:
    return st.session_state.api_base_url.rstrip("/")


def call_health_api(api_base_url: str) -> Dict[str, Any]:
    r = requests.get(f"{api_base_url}/health", timeout=10)
    r.raise_for_status()
    return r.json()


def call_ingest_api(api_base_url, user_id, uploaded_file) -> Dict[str, Any]:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    r = requests.post(f"{api_base_url}/ingest", data={"user_id": user_id}, files=files, timeout=300)
    r.raise_for_status()
    return r.json()


def call_ask_api(api_base_url, user_id, query) -> Dict[str, Any]:
    r = requests.post(f"{api_base_url}/ask", json={"user_id": user_id, "query": query}, timeout=300)
    r.raise_for_status()
    return r.json()


# -------------------------------------------------------------------
# Top banner
# -------------------------------------------------------------------

st.markdown(
    """
    <div class="top-banner">
        <h1>🏥 Health Assistant</h1>
        <p>Upload your health documents · Ask questions · Book appointments</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Settings (collapsed by default — non-technical users won't need it)
# -------------------------------------------------------------------

with st.expander("⚙️ Settings (tap to open)", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        new_url = st.text_input("Server address", value=st.session_state.api_base_url)
        st.session_state.api_base_url = new_url.rstrip("/")
    with col_b:
        new_uid = st.text_input("Your ID", value=st.session_state.user_id)
        st.session_state.user_id = new_uid.strip() or "user123"

    if st.button("Check connection"):
        try:
            call_health_api(get_api_base_url())
            st.markdown('<div class="ok-banner">✅ Connected successfully.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="err-banner">❌ Could not connect: {e}</div>', unsafe_allow_html=True)


# -------------------------------------------------------------------
# How it works — visible to new / non-technical users
# -------------------------------------------------------------------

with st.expander("ℹ️ How to use this app", expanded=False):
    st.markdown(
        """
        <div class="step-row">
            <div class="step-badge">1</div>
            <div class="step-text"><b>Upload your document</b> — health report, prescription, or any medical file (PDF, Word, or text).</div>
        </div>
        <div class="step-row">
            <div class="step-badge">2</div>
            <div class="step-text"><b>Ask a question</b> — type what you want to know, in plain words. For example: <i>"What medication is listed for me?"</i></div>
        </div>
        <div class="step-row">
            <div class="step-badge">3</div>
            <div class="step-text"><b>Book an appointment</b> — just ask: <i>"Schedule an appointment for me on July 1."</i></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.divider()


# -------------------------------------------------------------------
# Tabs
# -------------------------------------------------------------------

tab_ask, tab_upload, tab_history = st.tabs(
    ["💬 Ask a Question", "📄 Upload a Document", "🕘 Past Questions"]
)


# ══════════════════════════════════════════════════════════════════
# TAB 1 — Ask
# ══════════════════════════════════════════════════════════════════

with tab_ask:

    st.markdown('<div class="section-label">What would you like to know?</div>', unsafe_allow_html=True)

    # Quick-tap example buttons
    st.markdown("**Quick examples — tap to use:**")
    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        if st.button("📋 Show my reports"):
            st.session_state["prefill_query"] = "Give me the reports for the current user"
        if st.button("💊 Medication details"):
            st.session_state["prefill_query"] = "What medication is mentioned for diabetes?"
    with ex_col2:
        if st.button("📅 Check appointments"):
            st.session_state["prefill_query"] = "Check available appointments"
        if st.button("🗓️ Book appointment"):
            st.session_state["prefill_query"] = "Schedule an appointment for me on 2026-07-01"

    prefill = st.session_state.pop("prefill_query", "")

    query = st.text_area(
        "Type your question here",
        value=prefill,
        placeholder="Example: What does my blood test report say?",
        height=110,
        label_visibility="collapsed",
    )

    ask_clicked = st.button("🔍 Get Answer", type="primary")

    if ask_clicked:
        if not query.strip():
            st.markdown('<div class="err-banner">Please type a question first.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Finding your answer…"):
                try:
                    result = call_ask_api(
                        api_base_url=get_api_base_url(),
                        user_id=st.session_state.user_id,
                        query=query.strip(),
                    )

                    st.session_state.chat_history.append(result)

                    selected_tool = result.get("selected_tool", "")
                    answer = result.get("answer", "")
                    tool_result = result.get("tool_result", {})

                    # ── Answer ──
                    tool_label = "📄 Document search" if selected_tool == "rag_tool" else "📅 Appointment system"
                    st.markdown(
                        f"""
                        <div class="answer-box">
                            <div class="tool-tag">{tool_label}</div><br>
                            {answer}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # ── RAG chunks ──
                    if selected_tool == "rag_tool":
                        rag_results = tool_result.get("results", [])
                        if rag_results:
                            st.markdown('<div class="section-label">📑 Where this came from</div>', unsafe_allow_html=True)
                            for i, item in enumerate(rag_results, 1):
                                content = item.get("content", "")
                                meta = item.get("metadata", {})
                                st.markdown(
                                    f"""
                                    <div class="chunk-card">
                                        <b>Excerpt {i}</b> &nbsp;·&nbsp; Page {meta.get("page", "?")} &nbsp;·&nbsp; File: {meta.get("uploaded_filename", "?")}
                                        <hr style="border:none;border-top:1px solid #e2e8f0;margin:0.6rem 0">
                                        {content[:600]}{"…" if len(content) > 600 else ""}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                    # ── Appointment results ──
                    elif selected_tool == "appointment_scheduler_tool":
                        booked = tool_result.get("appointment")
                        slots = tool_result.get("available_slots", [])

                        if booked:
                            st.markdown('<div class="section-label">✅ Your Appointment</div>', unsafe_allow_html=True)
                            st.markdown(
                                f"""
                                <div class="appt-card">
                                    <h4>🩺 {booked.get("doctor", "Doctor")}</h4>
                                    <p>📅 {booked.get("date", "—")} &nbsp; 🕐 {booked.get("time", "—")}</p>
                                    <p>Specialization: {booked.get("specialization", "—")}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        if slots:
                            st.markdown('<div class="section-label">📅 Available Slots</div>', unsafe_allow_html=True)
                            for slot in slots:
                                status_icon = "🟢 Available" if slot.get("available") else "🔴 Booked"
                                st.markdown(
                                    f"""
                                    <div class="appt-card">
                                        <h4>🩺 {slot.get("doctor", "Doctor")}</h4>
                                        <p>📅 {slot.get("date", "—")} &nbsp; 🕐 {slot.get("time", "—")}</p>
                                        <p>Specialization: {slot.get("specialization", "—")} &nbsp;·&nbsp; {status_icon}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                    with st.expander("🔬 Full technical details"):
                        st.json(result)

                except requests.exceptions.HTTPError as e:
                    try:
                        detail = e.response.json()
                    except Exception:
                        detail = str(e)
                    st.markdown(f'<div class="err-banner">❌ Something went wrong: {detail}</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f'<div class="err-banner">❌ Could not connect to server: {e}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 2 — Upload
# ══════════════════════════════════════════════════════════════════

with tab_upload:

    st.markdown('<div class="section-label">Upload a health document</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="info-banner">
            📌 Accepted file types: <b>PDF, Word (.docx), or Text (.txt)</b><br>
            After uploading, you can ask questions about the document in the <b>Ask a Question</b> tab.
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose your file",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        st.markdown(
            f"""
            <div class="simple-card">
                📄 &nbsp;<b>{uploaded_file.name}</b><br>
                <span style="color:#64748b;font-size:0.9rem">Size: {uploaded_file.size / 1024:.1f} KB &nbsp;·&nbsp; Type: {uploaded_file.type or "unknown"}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("📤 Upload and Save", type="primary"):
            with st.spinner("Uploading… this may take a moment."):
                try:
                    result = call_ingest_api(
                        api_base_url=get_api_base_url(),
                        user_id=st.session_state.user_id,
                        uploaded_file=uploaded_file,
                    )
                    st.markdown(
                        '<div class="ok-banner">✅ Your document has been saved. You can now ask questions about it.</div>',
                        unsafe_allow_html=True,
                    )
                    with st.expander("Technical details"):
                        st.json(result)

                except requests.exceptions.HTTPError as e:
                    try:
                        detail = e.response.json()
                    except Exception:
                        detail = str(e)
                    st.markdown(f'<div class="err-banner">❌ Upload failed: {detail}</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f'<div class="err-banner">❌ Upload failed: {e}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2rem 0;font-size:0.95rem;">No file chosen yet. Tap the button above to select a file.</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════
# TAB 3 — History
# ══════════════════════════════════════════════════════════════════

with tab_history:

    st.markdown('<div class="section-label">Your past questions</div>', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2.5rem 0;font-size:0.95rem;">No questions asked yet. Start by typing a question in the <b>Ask a Question</b> tab.</div>',
            unsafe_allow_html=True,
        )
    else:
        if st.button("🗑️ Clear history"):
            st.session_state.chat_history = []
            st.rerun()

        for i, item in enumerate(reversed(st.session_state.chat_history), 1):
            q = item.get("query", "")
            tool = item.get("selected_tool", "")
            ans = item.get("answer", "")
            tool_label = "📄 Documents" if tool == "rag_tool" else "📅 Appointments"

            with st.expander(f"Q{i}: {q[:70]}{'…' if len(q) > 70 else ''}", expanded=(i == 1)):
                st.markdown(f"**Your question:** {q}")
                st.markdown(f"**Source:** {tool_label}")
                st.markdown("**Answer:**")
                st.markdown(
                    f'<div class="simple-card">{ans}</div>',
                    unsafe_allow_html=True,
                )


# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------

st.markdown(
    """
    <div class="footer-note">
        ⚕️ This tool is for information only. Always consult a real doctor for medical advice.
    </div>
    """,
    unsafe_allow_html=True,
)