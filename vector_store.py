import faiss
import numpy as np


class VectorStore:
    def __init__(self, embedding_dim: int):
        # Exact L2 distance index
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.chunks = []

    def add_chunks(self, chunks):
        """
        Adds embedded chunks to FAISS index.
        """
        if not chunks:
            return

        embeddings = np.array(
            [chunk["embedding"] for chunk in chunks],
            dtype="float32"
        )

        self.index.add(embeddings)
        self.chunks.extend(chunks)

    def search(self, query_embedding, top_k=5):
        """
        Searches for top_k similar chunks.
        """
        if getattr(self.index, "ntotal", 0) == 0:
            return []

        query_embedding = np.array([query_embedding], dtype="float32")

        _distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                results.append(self.chunks[idx])

        return results

# debug change
