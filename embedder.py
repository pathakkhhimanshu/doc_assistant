from sentence_transformers import SentenceTransformer

# Load once (important)
_model = None


def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_chunks(chunks):
    """
    Takes a list of chunk dicts and adds embeddings to each.
    """
    model = get_embedder()

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb

    return chunks

# debug change
