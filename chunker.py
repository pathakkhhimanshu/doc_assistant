def chunk_text(
    text: str,
    doc_name: str,
    page_number: int,
    chunk_size: int = 220,
    overlap: int = 40
):
    """
    Splits text into overlapping word chunks.
    Returns list of chunks with metadata.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_text: chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_text: overlap must be >= 0 and < chunk_size")

    words = text.split()
    chunks = []

    start = 0
    chunk_id = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]

        chunk_text = " ".join(chunk_words)

        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "doc_name": doc_name,
            "page": page_number
        })

        chunk_id += 1
        start += chunk_size - overlap

    return chunks

# debug change
