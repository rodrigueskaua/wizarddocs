from typing import Protocol

class Embedder(Protocol):
  name: str
  dimensions: int

  def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
  def embed_query(self, text: str) -> list[float]: ...
