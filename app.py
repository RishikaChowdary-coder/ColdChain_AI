import streamlit as st
from pathlib import Path
from config import APP_NAME, APP_TAGLINE, DEFAULT_SOP_PATH, ensure_directories, get_settings
from document_manager import list_pdf_documents, save_uploaded_pdf, remove_document
from rag_engine import ColdChainRAG, ConfigurationError, RAGError

st.set_page_config(page_title="ColdChain AI", page_icon="🧊", layout="wide", initial_sidebar_state="expanded")
ensure_directories()
settings = get_settings()

st.markdown("""
<style>
:root { --forest:#071A14; --emerald:#2E8B68; --sage:#8FBF9F; --purple:#B7A6D9; --ice:#A9D9E8; --warm:#F3F8F4; }
.stApp { background: linear-gradient(145deg, #f5f8f5 0%, #edf5f0 55%, #f6f3fa 100%); color:#14231b; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#071A14 0%,#10382a 100%); }
[data-testid="stSidebar"] * { color:#F3F8F4 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .42rem .55rem; border-radius: .65rem; }
.block-container { padding-top: 1.7rem; max-width: 1440px; }
.hero { background: linear-gradient(120deg,#071A14 0%,#14553e 70%,#2E8B68 100%); color:#F3F8F4; border-radius:22px; padding:2rem 2.2rem; margin-bottom:1.1rem; }
.hero h1 { color:#F3F8F4; font-size:2.25rem; margin-bottom:.35rem; }
.hero p { color:#dcece2; font-size:1.05rem; }
.eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; color:#8FBF9F; }
.panel { background:rgba(255,255,255,.84); border:1px solid #dce8df; border-radius:16px; padding:1rem 1.15rem; margin:.25rem 0 .8rem; box-shadow:0 5px 20px rgba(7,26,20,.035); }
.panel h3 { margin-top:.1rem; }
.pill { display:inline-block; border-radius:99px; padding:.24rem .65rem; background:#e1f1e8; color:#216b4a; font-size:.78rem; font-weight:700; }
.small-muted { color:#607367; font-size:.88rem; }
div.stButton > button { border-radius:10px; border:1px solid #cbded1; font-weight:650; }
div.stButton > button[kind="primary"] { background:#2E8B68; border-color:#2E8B68; }
[data-testid="stMetric"] { background:rgba(255,255,255,.8); border:1px solid #dce8df; padding:1rem; border-radius:14px; }
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
pages = ["Dashboard", "Ask AI", "SOP Knowledge Base", "Cold Storage Workflow", "RAG Trace", "Responsible AI", "Settings"]

with st.sidebar:
    st.markdown("## 🧊 ColdChain AI")
    st.caption("Understand your cold chain. Smarter.")
    st.divider()
    page = st.radio("Navigate", pages, label_visibility="collapsed")
    st.divider()
    st.markdown("**System overview**")
    st.caption(f"RAG: {'Ready' if engine.is_ready else 'Not initialized'}")
    st.caption(f"Documents: {len(engine.documents)}")
    if settings.get("provider") == "ollama":
        st.success("Local AI model connected")
    elif not settings.get("google_api_key"):
        st.warning("API key not configured")
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
            st.session_state["nav_target"] = "Ask AI"
            st.rerun()
    with c2:
        if st.button("↗ Explore workflow", use_container_width=True):
            st.session_state["nav_target"] = "Cold Storage Workflow"
            st.rerun()
    # Keep radio state simple; the navigation target is reflected in a quick action below.
    if st.session_state.get("nav_target"):
        st.info(f"Choose **{st.session_state.nav_target}** in the sidebar to continue.")
        st.session_state.nav_target = None

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
    steps = st.columns(4)
    for col, (num, title, desc) in zip(steps, [
        ("01", "SOP document", "Load approved PDF guidance."),
        ("02", "Retrieve", "Find relevant passages with embeddings."),
        ("03", "Generate", "Gemini explains only from retrieved context."),
        ("04", "Verify", "Review source document and page references."),
    ]):
        with col:
            st.markdown(f'<div class="panel"><div class="eyebrow">{num}</div><h3>{title}</h3><div class="small-muted">{desc}</div></div>', unsafe_allow_html=True)
    st.subheader("Try asking")
    qs = ["Why is temperature monitoring important?", "Explain the cold-storage workflow.", "What does the SOP say about receiving?", "What handling rules are documented for perishables?"]
    qcols = st.columns(2)
    for i, q in enumerate(qs):
        with qcols[i % 2]:
            if st.button(q, key=f"sample_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.session_state["nav_target"] = "Ask AI"
                st.info("Choose **Ask AI** in the sidebar. Your question is ready.")
    st.info("Only indexed SOP content can support grounded answers. A missing source is not proof that a procedure does not exist.")

elif page == "Ask AI":
    hero("Ask ColdChain AI", "Ask questions about your uploaded cold-storage SOPs and inspect the evidence behind each answer.", "GROUNDED ANSWERS")
    if not engine.is_ready:
        st.warning("Your knowledge base is not ready yet. Add a PDF and configure GOOGLE_API_KEY in Settings or your .env file.")
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
    st.markdown('<div class="panel"><b>Supported format:</b> PDF. Documents are processed into text chunks and embeddings before they can be used for answers.</div>', unsafe_allow_html=True)
    upload = st.file_uploader("Upload SOP PDF", type=["pdf"], accept_multiple_files=True)
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
                    st.info("Choose **Ask AI** in the sidebar to submit this question.")

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
