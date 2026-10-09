import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

DEFAULT_SOP_PATH = DATA_DIR / "Cold_Storage_SOP.pdf"

APP_NAME = "ColdChain AI"
APP_TAGLINE = "Understand your cold chain. Smarter."


def ensure_directories():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_settings():
    load_dotenv(PROJECT_ROOT / ".env")

    return {
        "provider": os.getenv("LLM_PROVIDER", "ollama"),

        "ollama_base_url": os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434"
        ),

        "ollama_chat_model": os.getenv(
            "OLLAMA_CHAT_MODEL",
            "llama3.2:latest"
        ),

        "ollama_embedding_model": os.getenv(
            "OLLAMA_EMBEDDING_MODEL",
            "nomic-embed-text:latest"
        ),

        "google_api_key": os.getenv(
            "GOOGLE_API_KEY",
            ""
        ),

        "generation_model": os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        ),

        "embedding_model": os.getenv(
            "GEMINI_EMBEDDING_MODEL",
            "models/gemini-embedding-001"
        ),

        "chunk_size": int(
            os.getenv("CHUNK_SIZE", "900")
        ),

        "chunk_overlap": int(
            os.getenv("CHUNK_OVERLAP", "120")
        ),

        "retrieval_k": int(
            os.getenv("RETRIEVAL_K", "4")
        ),

        "max_upload_mb": int(
            os.getenv("MAX_UPLOAD_MB", "20")
        )
    }