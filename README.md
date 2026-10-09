# 🧊 ColdChain AI

ColdChain AI is a Streamlit application that uses LangChain, Google Gemini, embeddings, and retrieval-augmented generation (RAG) to explain uploaded cold-storage SOP documents in clear language.

It is an **informational and training assistant only**. It does not control warehouse equipment, change temperature settings, approve operations, or replace trained personnel.

## Features

- Streamlit multi-page interface: Dashboard, Ask AI, SOP Knowledge Base, Workflow, RAG Trace, Responsible AI, and Settings.
- PDF ingestion using LangChain `PyPDFLoader`.
- Chunking with `RecursiveCharacterTextSplitter`.
- Gemini embeddings and an in-memory vector store.
- Gemini answer generation grounded in retrieved SOP context.
- Source document and page references based on PDF metadata.
- PDF upload, index rebuilding, and removal of uploaded documents.
- RAG execution metadata and recent trace history.
- Friendly handling of missing configuration and common Gemini errors.

## Requirements

- Python 3.11 or 3.12 recommended.
- A Google AI Studio API key with access to the selected Gemini models.
- Internet connection for Gemini embeddings and generation.

## Setup on Windows PowerShell

Open PowerShell in the `ColdChain-AI` folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your own key:

```env
GOOGLE_API_KEY=your_actual_key_here
```

Never share or commit `.env`.

Place your starter SOP at:

```text
data/Cold_Storage_SOP.pdf
```

Or launch the app and upload a PDF in **SOP Knowledge Base**.

## Run

```powershell
streamlit run app.py
```

Open the local URL Streamlit prints in the terminal.

## Run tests

```powershell
python -m pytest -q
```

Offline tests do not need a live Gemini API call. Live API availability, quotas, and model access can vary.

## How RAG works

1. Load PDF pages and preserve page metadata.
2. Split text into chunks.
3. Generate embeddings for chunks.
4. Store chunks in `InMemoryVectorStore`.
5. Embed/search the user's question through the vector store.
6. Send retrieved context to Gemini.
7. Show the answer with document and page references derived from retrieved metadata.

## Important limitations

- The vector store is in memory and is rebuilt when the application session initializes or the index is rebuilt.
- Uploaded PDFs are stored under `data/uploads/`; that directory is ignored by Git.
- Scanned PDFs without extractable text require OCR, which is not included in this starter implementation.
- Model identifiers and quotas can change. If a configured model is unavailable, update the model name to one enabled for your API key.
- Similarity scores are not displayed unless the selected retrieval API provides a genuine score.
- Generated answers can still be incomplete or wrong. Verify safety-critical information against approved procedures.

## Project structure

```text
ColdChain-AI/
├── app.py
├── rag_engine.py
├── document_manager.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── backend_test.py
├── test_gemini.py
├── tests/
│   ├── test_document_processing.py
│   ├── test_retrieval.py
│   └── test_grounding.py
├── data/
│   └── Cold_Storage_SOP.pdf
└── assets/
    └── logo.svg
```

## Responsible use

ColdChain AI explains the uploaded documents. It does not operate equipment, change settings, or make operational decisions.
