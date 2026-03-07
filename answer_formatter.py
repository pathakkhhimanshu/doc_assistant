import re
from collections import OrderedDict


def clean_text(text: str) -> str:
    # Remove non-ASCII (Hindi, etc.)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text: str):
    return re.split(r"(?<=[.!?])\s+", text)


def format_answer(
    chunks,
    mode: str = "quick",   # quick | detailed
    bullets: bool = False
):
    """
    Takes retrieved chunks and returns:
    - clean student-style answer
    - source info (doc + pages)
    """

    # 1. Collect sentences without duplication
    seen = OrderedDict()

    sources = {}

    for chunk in chunks:
        text = clean_text(chunk["text"])
        sentences = split_sentences(text)

        for s in sentences:
            s = s.strip()
            if len(s) < 20:
                continue
            seen[s] = None

        # Track sources
        doc = chunk["doc_name"]
        page = chunk["page"]
        sources.setdefault(doc, set()).add(page)

    sentences = list(seen.keys())

    # 2. Control length based on mode
    if mode == "quick":
        sentences = sentences[:3]
    else:
        sentences = sentences[:8]

    # 3. Format output
    if bullets:
        answer_text = "\n".join(f"• {s}" for s in sentences)
    else:
        answer_text = " ".join(sentences)

    # 4. Format sources
    source_lines = []
    for doc, pages in sources.items():
        pages_str = ", ".join(str(p) for p in sorted(pages))
        source_lines.append(f"{doc} — Page {pages_str}")

    source_text = "\n".join(source_lines)

    return {
        "answer": answer_text,
        "sources": source_text
    }

# debug change
