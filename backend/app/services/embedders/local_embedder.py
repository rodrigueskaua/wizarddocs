from sentence_transformers import SentenceTransformer

class LocalEmbedder:
  name = "local"

  def __init__(self, model: str, query_prefix: str, document_prefix: str):
    self._model = SentenceTransformer(model)
    self._query_prefix = query_prefix or None
    self._document_prefix = document_prefix or None
    self.dimensions = self._model.get_embedding_dimension()

  def embed_documents(self, texts: list[str]) -> list[list[float]]:
    embeddings = self._model.encode_document(
      texts, prompt=self._document_prefix, normalize_embeddings=True
    )
    return embeddings.tolist()

  def embed_query(self, text: str) -> list[float]:
    embedding = self._model.encode_query(
      text, prompt=self._query_prefix, normalize_embeddings=True
    )
    return embedding.tolist()
