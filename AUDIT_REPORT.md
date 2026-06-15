# Codebase Audit Report

## 1. High-Severity & Security Vulnerabilities (The "Fix Right Now" List)

*   **Arbitrary File Write / Remote Code Execution (RCE)**
    *   **File:** `main.py`, Lines ~30-31 (`safe_filename`) and ~62-63 (`upload`).
    *   **Description:** The `safe_filename` function only normalizes Unicode characters but fails to strip directory traversal sequences like `../`. An attacker can upload a file named `../../../main.py` and overwrite the application's source code, leading to Remote Code Execution.
*   **Arbitrary File Read / Path Traversal**
    *   **File:** `main.py`, Lines ~75 (`select_doc`) and ~88 (`ask`).
    *   **Description:** The `select_doc` endpoint allows writing an arbitrary string to `current.txt`. The `/ask` route then reads this string and concatenates it with the `UPLOADS` directory to read a document. An attacker can set the document name to `../../../../etc/passwd` and exfiltrate sensitive server files via the `/ask` route (by forcing the search to match or erroring out with file contents).
*   **Global State Contamination / Broken Session Management**
    *   **File:** `main.py`, Line ~18 (`CURRENT = os.path.join(UPLOADS, "current.txt")`).
    *   **Description:** The active document state is maintained globally in a single `current.txt` file. This means there is zero isolation between users. If User A selects "Confidential.pdf" and User B asks a question, User B will query User A's document, causing massive data leakage.
*   **Cross-Site Scripting (XSS)**
    *   **File:** `templates/index.html` (Frontend) & `simple_search.py` (Backend).
    *   **Description:** The `/ask` route returns content directly extracted from PDFs. The frontend renders this using `answerBox.innerHTML = data.answer;`. A maliciously crafted PDF containing JavaScript payloads within its text could execute code in the victim's browser.

## 2. Logical Bugs & Edge Cases (The "Silent Killers")

*   **Hardcoded Exam Format Dependency**
    *   **File:** `simple_search.py` (`extract_qa_blocks`).
    *   **Description:** The application strictly expects the document to be in a specific Q&A format (e.g., `Q1. ... ?`). If a user uploads a standard document or book, `qa_blocks` will be empty, and the system will silently fail with "Answer not found in document" every time.
*   **Destructive Data Sanitization**
    *   **File:** `simple_search.py` (`clean_text`) and `answer_formatter.py`.
    *   **Description:** The line `re.sub(r"[^\x00-\x7F]+", " ", text)` unconditionally strips all non-ASCII characters. This destroys documents containing multilingual text, accents, special symbols, or mathematical equations.
*   **Resource Leaks & OOM Risks**
    *   **File:** `main.py` (`get_current_doc` and `upload`).
    *   **Description:** `open(CURRENT).read()` never explicitly closes the file handle. More critically, `await file.read()` in the upload endpoint loads the entire uploaded file into memory at once, making the server highly susceptible to Out of Memory (OOM) crashes via large file uploads.

## 3. Architecture, Scalability & Anti-Patterns

*   **Dead Code & Ghost Architecture**
    *   **Description:** The codebase includes an entire RAG (Retrieval-Augmented Generation) pipeline (`chunker.py`, `embedder.py`, `vector_store.py`, `retriever.py`, `gemini_rewriter.py`). However, `main.py` completely ignores them and uses a primitive regex-based `simple_search.py`. This is a massive architectural failure.
*   **Synchronous Blocking Calls in Asynchronous Routes**
    *   **Description:** The `async def ask` and `async def upload` routes in `main.py` utilize synchronous I/O functions (`open()`, `PyPDF2.PdfReader()`). This blocks the FastAPI ASGI event loop, meaning a single large PDF upload or query will stall the entire server for all other users.
*   **$O(N)$ Parsing Bottleneck (Zero Caching)**
    *   **Description:** On *every single query* to `/ask`, the entire PDF is re-read and parsed dynamically by `read_document`. Parsing PDFs is extremely CPU-bound and slow. This anti-pattern completely cripples scalability.

## 4. The "Exploit Scenario" (Proof of Concept)

**Scenario: Complete System Takeover via RCE and Global State**
1. **The Attack Vector:** An attacker discovers the file upload endpoint (`/upload`) and notices that filenames aren't properly sanitized.
2. **The Execution:** The attacker crafts a malicious Python script containing a reverse shell payload. They upload this file with the filename `../../../main.py`.
3. **The Catastrophe:** Because `safe_filename` merely normalizes Unicode, the `os.path.join` writes the malicious script directly over the application's actual `main.py`.
4. **The Trigger:** The application server (e.g., Uvicorn) detects a file change and hot-reloads, or a new worker is spawned. The attacker's code executes, granting them a reverse shell and full control over the host server. They can then pivot to internal networks or dump the database.

## 5. Actionable Remediation Plan

*   **Refactoring Steps:**
    1.  **Immediate:** Fix the path traversal vulnerabilities in `safe_filename` and document selection. Use `os.path.basename` to secure paths.
    2.  **Immediate:** Implement proper session management. Replace the global `current.txt` with user-specific sessions (e.g., signed cookies) to isolate document states.
    3.  **High Priority:** Replace the `innerHTML` assignment in the frontend with `textContent`, or use a sanitization library (like DOMPurify) before rendering HTML.
    4.  **High Priority:** Transition file uploads and reads to non-blocking I/O (e.g., `aiofiles` or `asyncio.to_thread`). Stream file uploads instead of reading them completely into memory.
    5.  **Medium Priority:** Remove the `simple_search` regex logic and integrate the actual RAG pipeline (`vector_store`, `embedder`). Index documents once upon upload, saving embeddings to FAISS, rather than reading PDFs on every request.

*   **Corrected Code Snippets:**

**Fix 1: Path Traversal (RCE) in `safe_filename`**
```python
import os
import re
import unicodedata

def safe_filename(name: str) -> str:
    """
    Securely sanitizes filenames to prevent path traversal and arbitrary file write.
    """
    # 1. Extract just the base filename, discarding any directory paths
    base = os.path.basename(name)
    # 2. Normalize unicode characters
    base = unicodedata.normalize("NFKD", base)
    # 3. Strip out any dangerous characters, allowing only alphanumeric, dot, dash, and underscore
    base = re.sub(r'[^a-zA-Z0-9.\-_]', '', base)

    if not base or base.startswith('.'):
        return "unnamed_upload.pdf"

    return base
```

**Fix 2: Global State Leakage / Session Isolation**
```python
# In main.py
from fastapi import Request, Response

# Re-route the active document logic to use secure client-side cookies
# rather than a global `current.txt` file.

@app.get("/select/{name}")
def select_doc(name: str, response: Response):
    """
    Isolate the selected document to the user's session.
    """
    # Ensure the requested document actually exists before setting it
    safe_name = safe_filename(name)
    if not os.path.exists(os.path.join(UPLOADS, safe_name)):
        return RedirectResponse("/", 303)

    response = RedirectResponse("/", 303)
    # Set an HttpOnly cookie to store the active document per user
    response.set_cookie(key="active_document", value=safe_name, httponly=True)
    return response

# Update the `get_current_doc` function to extract from the request:
def get_current_doc(request: Request):
    return request.cookies.get("active_document")
```
