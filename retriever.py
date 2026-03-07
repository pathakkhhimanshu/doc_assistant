from embedder import get_embedder
from vector_store import VectorStore


class SemanticRetriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.embedder = get_embedder()

    def retrieve(self, question: str, top_k: int = 5):
        """
        Given a user question, return top_k relevant chunks.
        """
        # 1. Embed the question
        query_embedding = self.embedder.encode(
            question,
            convert_to_numpy=True
        )

        # 2. Search in FAISS
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k
        )

        return results

# debug change
