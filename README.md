# Doc Assistant

A lightweight FastAPI app for asking questions over uploaded `.pdf` and `.txt` documents.

The app reads document text, stores the selected file in the current session, and returns an extractive answer based on keyword/sentence matching.

## Features

- Upload `.pdf` and `.txt` files
- Switch active document from the sidebar
- Ask questions in:
  - `quick` mode (short answer)
  - `detailed` mode (longer answer)
- Optional bullet-point answer formatting
- In-memory document text cache for faster repeated queries
- "New Session" action to clear uploaded files and cache

## Tech Stack

- Python 3.10+
- FastAPI + Uvicorn
- Jinja2 templates + static CSS/JS
- PyPDF2 for PDF text extraction

The repository also includes semantic-retrieval modules (`chunker.py`, `embedder.py`, `vector_store.py`, `retriever.py`) that can be used for FAISS + sentence-transformer based search.

## Project Structure

- `main.py` - FastAPI app and routes
- `reader.py` - PDF/TXT text extraction and cleanup
- `simple_search.py` - core answer selection logic
- `templates/index.html` - web UI
- `static/style.css` - frontend styling
- `uploads/` - runtime upload/session files
- `requirements.txt` - Python dependencies

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. (Optional) Create a `.env` file for future Gemini-based rewriting support:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run

```powershell
uvicorn main:app --reload
```

Open: `http://127.0.0.1:8000`

## API Endpoints

- `GET /` - Home page
- `POST /upload` - Upload a document and set it active
- `GET /select/{name}` - Select an uploaded document
- `POST /ask` - Submit a question (`question`, `mode`, `bullets`)
- `GET /new-session` - Clear uploaded files and reset session

## Notes

- Current answer generation is extractive (pulled from document text), not generative.
- UI has a delete link for documents, but there is currently no `/delete/{name}` route in `main.py`.
- Uploaded files are stored locally in `uploads/`.

## License

Add a license file if you plan to distribute this project.
