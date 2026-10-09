"""Basic local checks. These checks do not call Gemini."""
from config import get_settings
from document_manager import list_pdf_documents
from rag_engine import ColdChainRAG

def main():
    settings = get_settings()
    print("ColdChain AI backend configuration")
    print("Google API key configured:", bool(settings["google_api_key"]))
    paths = list_pdf_documents()
    print("PDF files found:", len(paths))
    for path in paths:
        print(" -", path)
    engine = ColdChainRAG()
    print("Engine initialized:", engine is not None)
    print("Index is ready:", engine.is_ready)
    print("To build the index, use the app's SOP Knowledge Base page or call engine.rebuild_from_paths(paths).")

if __name__ == "__main__":
    main()
