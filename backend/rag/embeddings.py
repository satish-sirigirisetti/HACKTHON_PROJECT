"""Embedding model boundary; no model downloads are performed at startup."""


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Create embeddings after a model/provider is deliberately configured."""
    raise NotImplementedError("Embedding provider configuration is planned for the RAG phase")