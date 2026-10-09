from pathlib import Path
import re
import uuid
from config import DATA_DIR, UPLOAD_DIR, ensure_directories, get_settings

def save_uploaded_pdf(uploaded_file) -> str:
    ensure_directories()
    settings = get_settings()
    raw_name = Path(uploaded_file.name).name
    if Path(raw_name).suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")
    max_bytes = settings["max_upload_mb"] * 1024 * 1024
    content = uploaded_file.getvalue()
    if not content:
        raise ValueError(f"{raw_name} is empty.")
    if len(content) > max_bytes:
        raise ValueError(f"{raw_name} exceeds the {settings['max_upload_mb']} MB upload limit.")
    # Avoid collisions and unsafe names.
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(raw_name).stem).strip("._") or "sop"
    destination = UPLOAD_DIR / f"{stem}_{uuid.uuid4().hex[:8]}.pdf"
    if not content.startswith(b"%PDF"):
        raise ValueError(f"{raw_name} does not appear to be a valid PDF.")
    destination.write_bytes(content)
    return str(destination)

def list_pdf_documents():
    ensure_directories()
    candidates = []
    default = DATA_DIR / "Cold_Storage_SOP.pdf"
    if default.exists():
        candidates.append(default)
    candidates.extend(sorted(UPLOAD_DIR.glob("*.pdf")))
    # De-duplicate while preserving order.
    return list(dict.fromkeys(str(p.resolve()) for p in candidates if p.is_file()))

def remove_document_file(path: str):
    p = Path(path).resolve()
    allowed_roots = [(DATA_DIR / "uploads").resolve()]
    if not any(p == root or root in p.parents for root in allowed_roots):
        raise ValueError("Only uploaded documents can be deleted from disk. The bundled default SOP is protected.")
    if p.exists() and p.is_file() and p.suffix.lower() == ".pdf":
        p.unlink()

def remove_document(document_id: str, document_records: dict):
    record = document_records.get(document_id)
    if not record:
        raise ValueError("Document was not found in the active index.")
    remove_document_file(record["path"])
