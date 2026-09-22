import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import streamlit as st
from app.components.sidebar import render_sidebar
from app.utils.ui_helpers import get_student_profile_data
from agents.tutor_agent.tutor_agent import RAGTutorAgent
from schemas.rag_schema import TutorQueryRequest

st.set_page_config(
    page_title="RAG Conceptual Tutor | AI Placement Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

student_id = st.session_state.get("student_id", 1)
profile = get_student_profile_data(student_id)

st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 2rem;">🤖 Grounded RAG Placement Tutor</h1>
            <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Pedagogical AI tutor backed by hybrid vector search and strict source citations to prevent hallucinations.
            </p>
        </div>
        <div>
            <span class="sidebar-status-chip">Grounded RAG: Active</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize conversation history
if "tutor_messages" not in st.session_state:
    st.session_state["tutor_messages"] = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am your AI Placement Tutor. Ask me any conceptual question about "
                "**Data Structures & Algorithms**, **DBMS & SQL**, **Operating Systems**, "
                "**Computer Networks**, or **System Design**.\n\n"
                "All answers are grounded in verified computer science placement notes with strict source citations."
            ),
            "citations": []
        }
    ]

# Preset Prompts
st.markdown("##### 💡 Suggested Technical Inquiries:")
col_p1, col_p2, col_p3, col_p4 = st.columns(4)

preset_query = None
with col_p1:
    if st.button("🌳 BST Time Complexities", use_container_width=True):
        preset_query = "What is the worst-case time complexity of searching in a Binary Search Tree and how do self-balancing trees mitigate this?"
with col_p2:
    if st.button("💾 ACID Properties in DBMS", use_container_width=True):
        preset_query = "Explain ACID properties in database management systems with real-world banking examples."
with col_p3:
    if st.button("⚙️ Deadlocks & Conditions", use_container_width=True):
        preset_query = "What are the four Coffman conditions required for a deadlock to occur in an operating system?"
with col_p4:
    if st.button("🐍 Python GIL & Threads", use_container_width=True):
        preset_query = "Explain the Global Interpreter Lock (GIL) in CPython and how it affects multithreading."

# Optional Topic Filter
with st.expander("⚙️ Retrieval Filtering & Settings"):
    topic_filter = st.selectbox(
        "Filter Knowledge Domain (Optional):",
        options=["All Domains", "Data Structures & Algorithms", "Database Management Systems", "Operating Systems", "SQL", "Computer Networks"],
        index=0
    )
    filter_arg = None if topic_filter == "All Domains" else topic_filter

# Render Conversation
for msg in st.session_state["tutor_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            with st.expander(f"📚 Verified Sources ({len(msg['citations'])} cited)"):
                for cit in msg["citations"]:
                    st.markdown(f"- **{cit.get('document_title', 'Curriculum Source')}** &nbsp;|&nbsp; Section: *{cit.get('section', 'General')}* &nbsp;|&nbsp; Relevance: `{cit.get('similarity_score', 0.85):.2f}`")

# Chat Input
user_input = st.chat_input("Ask a technical placement or conceptual question...")
active_query = preset_query or user_input

if active_query:
    # Append user prompt
    st.session_state["tutor_messages"].append({"role": "user", "content": active_query, "citations": []})
    with st.chat_message("user"):
        st.markdown(active_query)

    # Process via RAGTutorAgent
    with st.chat_message("assistant"):
        with st.spinner("Searching local knowledge base and synthesizing grounded response..."):
            agent = RAGTutorAgent()
            req = TutorQueryRequest(
                student_id=student_id,
                query=active_query,
                topic_context=filter_arg,
                chat_history=[]
            )
            response = agent.answer_query(req)

            st.markdown(response.answer)
            
            cit_data = [
                {
                    "document_title": c.document_title,
                    "section": c.section,
                    "similarity_score": c.similarity_score
                }
                for c in response.citations
            ]
            if cit_data:
                with st.expander(f"📚 Verified Sources ({len(cit_data)} cited)"):
                    for cit in cit_data:
                        st.markdown(f"- **{cit['document_title']}** &nbsp;|&nbsp; Section: *{cit['section']}* &nbsp;|&nbsp; Relevance: `{cit['similarity_score']:.2f}`")

            st.session_state["tutor_messages"].append({
                "role": "assistant",
                "content": response.answer,
                "citations": cit_data
            })

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
if st.button("🗑️ Clear Conversation History"):
    st.session_state["tutor_messages"] = [st.session_state["tutor_messages"][0]]
    st.rerun()
