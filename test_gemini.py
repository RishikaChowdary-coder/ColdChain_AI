"""Optional live Gemini connectivity test; makes an API request and may consume quota."""
from config import get_settings
from rag_engine import ConfigurationError, RAGError, ColdChainRAG

def main():
    settings = get_settings()
    if not settings["google_api_key"]:
        raise SystemExit("GOOGLE_API_KEY is missing. Configure .env first.")
    engine = ColdChainRAG()
    try:
        engine._initialize_models()
        response = engine._chat_model.invoke("Reply with exactly: ColdChain AI connection test successful.")
        print(getattr(response, "content", response))
    except (ConfigurationError, RAGError) as exc:
        raise SystemExit(str(exc))

if __name__ == "__main__":
    main()
