
import streamlit as st
from pathlib import Path
from config import APP_NAME, APP_TAGLINE, DEFAULT_SOP_PATH, ensure_directories, get_settings
from document_manager import list_pdf_documents, save_uploaded_pdf, remove_document
from rag_engine import ColdChainRAG, ConfigurationError, RAGError

st.set_page_config(page_title="ColdChain AI", page_icon="❄️", layout="wide", initial_sidebar_state="expanded")
ensure_directories()
settings = get_settings()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --forest:#142B4D; --forest2:#203C66; --emerald:#4F73D8; --sage:#9DB8F4;
  --warm:#F5F8FC; --ink:#1F3557; --muted:#71839C; --line:#DFE7F1;
}
html, body, button, input, textarea, label,
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"],
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
  font-family:'Inter',sans-serif !important;
}
/* Keep Streamlit's icon font intact: otherwise icon ligatures render as words like 'upload'. */
.material-icons, .material-symbols-rounded, .material-symbols-outlined,
[data-testid="stIconMaterial"], [data-testid="stFileUploader"] span.material-symbols-rounded {
  font-family:'Material Symbols Rounded','Material Icons',sans-serif !important;
  font-weight:normal !important;
  font-style:normal !important;
  letter-spacing:normal !important;
  text-transform:none !important;
  white-space:nowrap !important;
  word-wrap:normal !important;
  direction:ltr !important;
  -webkit-font-feature-settings:'liga' !important;
  -webkit-font-smoothing:antialiased;
}
.stApp { background:linear-gradient(135deg,#F8FAFE 0%,#EEF3FB 65%,#F4F6FC 100%); color:var(--ink); }
.block-container { max-width:1320px; padding-top:1.25rem; padding-bottom:2.5rem; }

.brand-lockup { display:flex; align-items:center; gap:12px; padding:8px 0 12px; }
.brand-mark { width:48px; height:48px; flex:0 0 48px; border-radius:14px; display:flex; align-items:center; justify-content:center; background:linear-gradient(145deg,rgba(255,255,255,.16),rgba(145,190,255,.07)); border:1px solid rgba(202,229,255,.28); box-shadow:0 8px 20px rgba(5,18,43,.16), inset 0 1px 0 rgba(255,255,255,.14); }
.brand-mark svg { width:38px; height:38px; display:block; }
.brand-copy { min-width:0; }
.brand-name { color:#F7FAFF; font-size:1.32rem; line-height:1.1; letter-spacing:-.055em; font-weight:800; white-space:nowrap; }
.brand-name span { color:#9EC8FF; margin-left:3px; font-weight:700; }
.brand-tagline { margin-top:6px; color:#BFD0EA; font-size:.57rem; font-weight:700; letter-spacing:.13em; white-space:nowrap; }

[data-testid="stSidebar"] { background:linear-gradient(180deg,var(--forest) 0%,var(--forest2) 100%); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#F8FAFF; }
[data-testid="stSidebar"] h2 { color:#F8FAFF !important; font-size:1.28rem !important; letter-spacing:-.025em; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#D5E1F4 !important; }
[data-testid="stSidebar"] hr { border-color:rgba(213,225,244,.18); }
[data-testid="stSidebar"] div.stButton > button { min-height:42px; border-radius:11px; color:#F8FAFF !important; background:rgba(255,255,255,.045) !important; border:1px solid rgba(157,184,244,.24) !important; text-align:left !important; justify-content:flex-start !important; padding:.55rem .85rem; transition:background .15s ease,border-color .15s ease; }
[data-testid="stSidebar"] div.stButton > button:hover { background:rgba(79,115,216,.28) !important; border-color:#9DB8F4 !important; }
[data-testid="stSidebar"] div.stButton > button[kind="primary"] { background:#4F73D8 !important; border-color:#4F73D8 !important; color:#fff !important; }
.hero { background:linear-gradient(115deg,#142B4D 0%,#203C66 62%,#4F73D8 100%); color:#F8FAFF; border-radius:20px; padding:1.6rem 1.85rem; margin:0 0 1.1rem; box-shadow:0 8px 24px rgba(31,53,87,.08); overflow-wrap:anywhere; }
.hero h1 { color:#F8FAFF !important; font-size:clamp(1.65rem,2.8vw,2.3rem); line-height:1.18; letter-spacing:-.04em; margin:.5rem 0 .6rem; }
.hero p { color:#E0E9F8 !important; font-size:1rem; line-height:1.55; margin-bottom:0; }
.eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.7rem; line-height:1.4; font-weight:800; color:#AFC4F5; }
.panel { background:rgba(255,255,255,.91); border:1px solid var(--line); border-radius:15px; padding:1rem 1.1rem; margin:.15rem 0 .65rem; box-shadow:0 4px 16px rgba(31,53,87,.045); }
.panel h3 { margin:.35rem 0 .45rem; font-size:1.12rem; line-height:1.3; letter-spacing:-.02em; }
.small-muted { color:var(--muted); font-size:.9rem; line-height:1.55; }
.pill { display:inline-block; border-radius:99px; padding:.24rem .65rem; background:#EAF0FF; color:#3156B5; font-size:.78rem; font-weight:700; }
div.stButton > button { min-height:42px; border-radius:10px; border:1px solid #D5DFEF; font-weight:600; white-space:normal; line-height:1.35; transition:all .15s ease; }
div.stButton > button:hover { border-color:#9DB8F4; color:#203C66; }
div.stButton > button[kind="primary"] { background:#4F73D8; border-color:#4F73D8; color:#fff; }
[data-testid="stMetric"] { background:rgba(255,255,255,.9); border:1px solid var(--line); padding:.8rem .95rem; border-radius:14px; box-shadow:0 3px 12px rgba(31,53,87,.035); }
[data-testid="stMetricLabel"] { color:#71839C; font-size:.86rem; }
[data-testid="stMetricValue"] { color:#1F3557; font-size:1.8rem; }
[data-testid="stChatMessage"] { border:1px solid #E0E7EF; border-radius:14px; padding:.85rem 1rem; }
h2, h3 { letter-spacing:-.025em; }
hr { border-color:#DFE7F1; }
/* PDF uploader: keep the native control readable and avoid button-label collisions */
[data-testid="stFileUploader"] { background:rgba(255,255,255,.72); border:1px solid #DFE7F1; border-radius:14px; padding:12px 14px; }
[data-testid="stFileUploader"] section { background:#F7F9FE; border:1px dashed #A9BDEB; border-radius:11px; padding:12px; }
[data-testid="stFileUploader"] section > div { gap:.6rem; }
[data-testid="stFileUploader"] button { min-height:38px !important; border-radius:9px !important; background:#ffffff !important; color:#203C66 !important; border:1px solid #D5DFEF !important; padding:.45rem .8rem !important; white-space:nowrap !important; }
[data-testid="stFileUploader"] button p { color:#203C66 !important; margin:0 !important; white-space:nowrap !important; }
[data-testid="stFileUploader"] small { color:#71839C !important; }
[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p { color:#71839C; }
@media (max-width: 900px) { .hero { padding:1.25rem; } .block-container { padding-top:.9rem; } }
</style>
""", unsafe_allow_html=True)

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = ColdChainRAG()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "traces" not in st.session_state:
    st.session_state.traces = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

engine: ColdChainRAG = st.session_state.rag_engine
# Sidebar navigation grouped into sections
NAV_GROUPS = {
    "MAIN WORKSPACE": [
        "Dashboard",
        "Ask AI",
        "SOP Knowledge Base",
    ],
    "WORKFLOW & TRUST": [
        "Cold Storage Workflow",
        "Responsible AI",
    ],
    "DEVELOPER TOOLS": [
        "RAG Trace",
        "Settings",
    ],
}

pages = [page for group in NAV_GROUPS.values() for page in group]

with st.sidebar:
    # Refined brand lockup: ice-cube mark + carefully spaced wordmark.
    st.markdown("""
    <div class="brand-lockup">
        <div class="brand-mark" aria-label="ColdChain AI ice cube logo">
            <svg viewBox="0 0 64 64" role="img" aria-hidden="true">
                <defs>
                    <linearGradient id="iceFront" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stop-color="#DDF5FF"/>
                        <stop offset="100%" stop-color="#79B9F5"/>
                    </linearGradient>
                    <linearGradient id="iceSide" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stop-color="#8CCBFF"/>
                        <stop offset="100%" stop-color="#4D83D7"/>
                    </linearGradient>
                </defs>
                <path d="M32 5 54 17.5 32 30 10 17.5Z" fill="#F2FBFF" stroke="#C6E8FF" stroke-width="1.5"/>
                <path d="M10 17.5 32 30 32 56 10 43.5Z" fill="url(#iceFront)" stroke="#C6E8FF" stroke-width="1.5"/>
                <path d="M54 17.5 32 30 32 56 54 43.5Z" fill="url(#iceSide)" stroke="#A5D7FF" stroke-width="1.5"/>
                <path d="M32 5 32 30" stroke="#D5F0FF" stroke-width="1.4" opacity=".9"/>
                <path d="M17 21.5 27 27" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".9"/>
                <path d="M38 34 47 29" stroke="#EAF8FF" stroke-width="2" stroke-linecap="round" opacity=".8"/>
                <path d="M17 37 25 41.5" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".65"/>
            </svg>
        </div>
        <div class="brand-copy">
            <div class="brand-name">ColdChain<span>AI</span></div>
            <div class="brand-tagline">COLD STORAGE INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Preserve the currently selected page across reruns
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Dashboard"

    for group_name, group_pages in NAV_GROUPS.items():
        st.markdown(
            f"""
            <div style="
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                color: #AFC4F5;
                margin-top: 1.1rem;
                margin-bottom: 0.4rem;
            ">
                {group_name}
            </div>
            """,
            unsafe_allow_html=True,
        )

        for item in group_pages:
            if st.button(
                item,
                key=f"nav_{item}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.selected_page == item
                    else "secondary"
                ),
            ):
                st.session_state.selected_page = item
                st.rerun()

    page = st.session_state.selected_page

    st.divider()
    st.markdown("**System overview**")
    st.caption(f"RAG: {'Ready' if engine.is_ready else 'Not initialized'}")
    st.caption(f"Documents: {len(engine.documents)}")

    if settings.get("provider") == "ollama":
        st.caption("Provider: Ollama")
    elif settings.get("google_api_key"):
        st.caption("Provider: Gemini • Credentials configured")
    else:
        st.caption("Provider credentials missing")

    st.markdown("---")
    st.caption("Informational use only • No equipment control")
def hero(title, subtitle, eyebrow="COLDCHAIN INTELLIGENCE"):
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def panel(title, body):
    st.markdown(f'<div class="panel"><h3>{title}</h3>{body}</div>', unsafe_allow_html=True)

def initialize_default_if_present():
    path = Path(DEFAULT_SOP_PATH)
    if path.exists() and path.suffix.lower() == ".pdf" and not engine.documents:
        try:
            engine.index_paths([path])
        except Exception:
            pass

initialize_default_if_present()

if page == "Dashboard":
    hero("Your Cold Storage Intelligence Assistant", "Turn complex SOP documents into clear, grounded explanations.", "DOCUMENT INTELLIGENCE • POWERED BY RAG")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("✨ Ask ColdChain AI", type="primary", use_container_width=True):
            st.session_state.pending_question = ""
            st.session_state.selected_page = "Ask AI"
            st.rerun()
    with c2:
        if st.button("↗ Explore workflow", use_container_width=True):
            st.session_state.selected_page = "Cold Storage Workflow"
            st.rerun()
    stats = engine.stats()
    cols = st.columns(4)
    metrics = [
        ("Documents", stats["documents"], "PDFs in active knowledge base"),
        ("Pages", stats["pages"], "Pages successfully indexed"),
        ("Chunks", stats["chunks"], "Retrievable text passages"),
        ("RAG status", "Ready" if engine.is_ready else "Not ready", "Requires indexed documents and API configuration"),
    ]
    for col, (label, value, helptext) in zip(cols, metrics):
        with col:
            st.metric(label, value, help=helptext)
    st.subheader("How ColdChain AI works")
    process_steps = [
        ("01", "SOP document", "Load approved PDF guidance."),
        ("02", "Retrieve", "Find relevant passages with embeddings."),
        ("03", "Generate", "The configured language model explains retrieved evidence."),
        ("04", "Verify", "Review source documents and page references."),
    ]
    for idx in range(0, len(process_steps), 2):
        step_cols = st.columns(2, gap="medium")
        for col, (num, title, desc) in zip(step_cols, process_steps[idx:idx + 2]):
            with col:
                st.markdown(f'<div class="panel"><div class="eyebrow">STEP {num}</div><h3>{title}</h3><div class="small-muted">{desc}</div></div>', unsafe_allow_html=True)
    st.subheader("Try asking")
    qs = ["Why is temperature monitoring important?", "Explain the cold-storage workflow.", "What does the SOP say about receiving?", "What handling rules are documented for perishables?"]
    qcols = st.columns(2)
    for i, q in enumerate(qs):
        with qcols[i % 2]:
            if st.button(q, key=f"sample_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.session_state.selected_page = "Ask AI"
                st.rerun()
    st.info("Only indexed SOP content can support grounded answers. A missing source is not proof that a procedure does not exist.")

elif page == "Ask AI":
    hero("Ask ColdChain AI", "Ask questions about your uploaded cold-storage SOPs and inspect the evidence behind each answer.", "GROUNDED ANSWERS")
    if not engine.is_ready:
        provider = str(settings.get("provider", "ollama")).lower()
        if provider == "ollama":
            st.warning("Your knowledge base is not ready yet. Check that Ollama is running, the configured models are available, and a PDF has been indexed.")
        else:
            st.warning("Your knowledge base is not ready yet. Check the hosted model credentials and index at least one SOP PDF.")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧊" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📚 View source evidence"):
                    for src in msg["sources"]:
                        st.markdown(f"**{src['document']} — page {src['page']}**")
                        st.caption(src.get("excerpt", ""))
    with st.container():
        st.markdown("**Suggested questions**")
        suggestions = st.columns(3)
        suggested = ["Explain the workflow", "Temperature monitoring", "Perishable handling"]
        for i, q in enumerate(suggested):
            with suggestions[i]:
                if st.button(q, key=f"suggest_{i}", use_container_width=True):
                    st.session_state.pending_question = q
    prompt = st.chat_input("Ask a question about the uploaded SOP…")
    pending = st.session_state.get("pending_question", "")
    question = prompt or pending
    if question:
        st.session_state.pending_question = ""
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)
        with st.chat_message("assistant", avatar="🧊"):
            with st.spinner("Searching SOP evidence and preparing an explanation…"):
                try:
                    result = engine.ask(question)
                    answer = result["answer"]
                    st.markdown(answer)
                    if result["sources"]:
                        with st.expander("📚 View source evidence", expanded=True):
                            for src in result["sources"]:
                                st.markdown(f"**{src['document']} — page {src['page']}**")
                                st.caption(src.get("excerpt", ""))
                    else:
                        st.caption("No source pages were returned.")
                    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": result["sources"]})
                    st.session_state.last_result = result
                    st.session_state.traces.insert(0, result["trace"])
                    st.session_state.traces = st.session_state.traces[:10]
                except (ConfigurationError, RAGError) as e:
                    message = str(e)
                    st.error(message)
                    st.session_state.messages.append({"role": "assistant", "content": message, "sources": []})
                except Exception:
                    st.error("Something went wrong while processing the question. Check the terminal logs and your API configuration.")
        st.rerun()
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.last_result = None
        st.rerun()

elif page == "SOP Knowledge Base":
    hero("SOP Knowledge Base", "Upload, index, inspect, and manage the documents that ground ColdChain AI.", "DOCUMENT MANAGEMENT")
    st.markdown('<div class="panel"><b>Supported format: PDF</b><div class="small-muted">Documents are processed into searchable text chunks and embeddings before they can support answers.</div></div>', unsafe_allow_html=True)
    upload = st.file_uploader(
        "Choose SOP documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF documents containing your approved SOPs."
    )
    if upload and st.button("Upload and index selected PDFs", type="primary"):
        with st.spinner("Validating documents, extracting text, and creating embeddings…"):
            try:
                paths = [save_uploaded_pdf(f) for f in upload]
                engine.rebuild_from_paths([Path(p) for p in paths])
                st.success(f"Indexed {len(paths)} document(s) successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Indexing failed: {e}")
    stats = engine.stats()
    a, b, c = st.columns(3)
    a.metric("Indexed documents", stats["documents"])
    b.metric("Pages", stats["pages"])
    c.metric("Knowledge chunks", stats["chunks"])
    st.subheader("Active documents")
    docs = engine.document_details()
    if not docs:
        st.info("No documents indexed yet. Upload a PDF above, or place Cold_Storage_SOP.pdf in the data folder and restart the app.")
    for doc in docs:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{doc['name']}**")
                st.caption(f"{doc['pages']} pages • {doc['chunks']} chunks • {doc['status']}")
            with col2:
                if st.button("Remove", key=f"remove_{doc['id']}"):
                    try:
                        engine.remove_document(doc["id"])
                        st.success("Document removed from the active knowledge base.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    if st.button("Rebuild index from available PDFs"):
        all_paths = list_pdf_documents()
        if not all_paths:
            st.warning("No PDFs found in the data directory.")
        else:
            try:
                with st.spinner("Rebuilding knowledge base…"):
                    engine.rebuild_from_paths([Path(p) for p in all_paths])
                st.success("Knowledge base rebuilt.")
                st.rerun()
            except Exception as e:
                st.error(f"Rebuild failed: {e}")

elif page == "Cold Storage Workflow":
    hero("Cold Storage Workflow", "Explore common stages and ask questions grounded in the SOP.", "PROCESS EXPLAINER")
    st.info("This workflow is an educational overview, not an automated operating procedure. Follow your approved SOP and authorized personnel.")
    stages = [
        ("📥", "Receiving", "Understand what the available SOP says about receiving incoming goods."),
        ("🔎", "Inspection", "Explore documented inspection checks and incoming-goods requirements."),
        ("🌡️", "Temperature Monitoring", "Find the SOP's documented temperature monitoring guidance."),
        ("❄️", "Storage", "Review documented storage conditions and handling guidance."),
        ("📦", "Handling", "Explore documented rules for handling temperature-sensitive products."),
        ("🚚", "Dispatch", "Find the available documentation about dispatch procedures."),
    ]
    for idx in range(0, len(stages), 2):
        cols = st.columns(2)
        for col, stage in zip(cols, stages[idx:idx+2]):
            emoji, title, desc = stage
            with col:
                st.markdown(f'<div class="panel"><div style="font-size:1.7rem">{emoji}</div><h3>{title}</h3><div class="small-muted">{desc}</div></div>', unsafe_allow_html=True)
                if st.button(f"Ask about {title}", key=f"workflow_{title}", use_container_width=True):
                    st.session_state.pending_question = f"What does the uploaded SOP say about {title.lower()}?"
                    st.session_state.selected_page = "Ask AI"
                    st.rerun()

elif page == "RAG Trace":
    hero("RAG Trace", "Inspect the actual evidence retrieval behind your latest answer.", "TRANSPARENT AI")
    trace = st.session_state.last_result
    if not trace:
        st.info("No live RAG trace yet. Ask a question in Ask AI to populate this page. The example pipeline below is illustrative only.")
        st.markdown("""
        `User question` → `Query embedding` → `Vector search` → `Retrieved SOP chunks` → `Gemini generation` → `Answer + source pages`
        """)
    else:
        tr = trace["trace"]
        cols = st.columns(4)
        cols[0].metric("Retrieved chunks", tr.get("retrieved_chunks", 0))
        cols[1].metric("Retrieval time", f"{tr.get('retrieval_ms', 0)} ms")
        cols[2].metric("Generation time", f"{tr.get('generation_ms', 0)} ms")
        cols[3].metric("Status", tr.get("status", "unknown").title())
        st.markdown("**Question**")
        st.write(tr.get("question", ""))
        st.markdown("**Models**")
        st.write(f"Embedding: `{tr.get('embedding_model', 'unknown')}`  ·  Generation: `{tr.get('generation_model', 'unknown')}`")
        st.markdown("**Retrieved evidence**")
        chunks = trace.get("retrieved_chunks", [])
        if not chunks:
            st.warning("No chunks were retrieved for this question.")
        for i, chunk in enumerate(chunks, start=1):
            with st.expander(f"Chunk {i} · {chunk.get('document', 'Unknown document')} · page {chunk.get('page', '?')}"):
                st.write(chunk.get("text", ""))
                score = chunk.get("score")
                st.caption(f"Similarity score: {score}" if score is not None else "Similarity score not exposed by the configured vector store.")
        st.markdown("**Answer**")
        st.write(trace.get("answer", ""))

    if st.session_state.traces:
        st.subheader("Recent trace history")
        for idx, item in enumerate(st.session_state.traces):
            with st.expander(f"{idx+1}. {item.get('question', 'Question')} — {item.get('status', 'unknown')}"):
                st.write(item.get("answer_preview", ""))

elif page == "Responsible AI":
    hero("Responsible AI", "Designed to explain, not control.", "SAFETY & LIMITATIONS")
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel"><h3>✅ What ColdChain AI does</h3><p>✓ Uses uploaded SOP information</p><p>✓ Retrieves relevant document passages</p><p>✓ Provides clear, grounded explanations</p><p>✓ Shows supporting source references</p><p>✓ Supports document understanding and training</p><p>✓ Acknowledges when evidence is insufficient</p></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><h3>🛡️ What ColdChain AI does not do</h3><p>✕ Control refrigeration equipment</p><p>✕ Change temperature settings</p><p>✕ Approve or reject operations</p><p>✕ Replace official SOPs or trained personnel</p><p>✕ Make autonomous operational decisions</p><p>✕ Guarantee every answer is complete or correct</p></div>', unsafe_allow_html=True)
    st.subheader("How grounding works")
    st.markdown("**Question → Retrieved evidence → Gemini explanation → Source references**")
    st.warning("Always verify safety-critical decisions against approved procedures and authorized personnel. An answer missing from the uploaded document does not mean the procedure does not exist.")

elif page == "Settings":
    hero("Settings", "Review configuration and system readiness without exposing secrets.", "APPLICATION CONFIGURATION")
    st.subheader("Connection status")
    st.write("Google API key:", "Configured" if settings["google_api_key"] else "Missing")
    st.write("Generation model:", settings["generation_model"])
    st.write("Embedding model:", settings["embedding_model"])
    st.write("Vector store:", "In-memory (temporary)")
    st.write("Indexed documents:", len(engine.documents))
    st.caption("API keys are never displayed. The in-memory index is rebuilt when the app session initializes or when you rebuild it.")
    st.subheader("RAG settings")
    st.write(f"Chunk size: {settings['chunk_size']} characters")
    st.write(f"Chunk overlap: {settings['chunk_overlap']} characters")
    st.write(f"Retrieval count: {settings['retrieval_k']}")
    if st.button("Rebuild knowledge index", type="primary"):
        paths = list_pdf_documents()
        if not paths:
            st.warning("No PDFs found in the data directory.")
        else:
            try:
                with st.spinner("Rebuilding index…"):
                    engine.rebuild_from_paths([Path(p) for p in paths])
                st.success("Index rebuilt successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Index rebuild failed: {e}")
    if st.button("Clear chat and trace history"):
        st.session_state.messages = []
        st.session_state.traces = []
        st.session_state.last_result = None
        st.success("Session history cleared.")
    st.subheader("System boundaries")
    st.caption("ColdChain AI is informational only. It does not operate warehouse equipment or make operational decisions.")

