from services.embedders import get_embedder

def embed_documents(texts: list[str]) -> list[list[float]]:
  return get_embedder().embed_documents(texts)

def embed_query(text: str) -> list[float]:
  return get_embedder().embed_query(text)
