from functools import lru_cache

from core.config import settings
from llm.base import LLMNotConfiguredError
from services.embedders.base import Embedder
from services.embedders.gemini_embedder import GeminiEmbedder
from services.embedders.local_embedder import LocalEmbedder

@lru_cache
def get_embedder() -> Embedder:
  if settings.embedding_provider == "gemini":
    if not settings.gemini_api_key:
      raise LLMNotConfiguredError(
        "EMBEDDING_PROVIDER=gemini exige GEMINI_API_KEY. Configure a chave ou volte para EMBEDDING_PROVIDER=local."
      )
    return GeminiEmbedder(
      api_key=settings.gemini_api_key,
      model=settings.gemini_embedding_model,
      dimensions=settings.embedding_dimensions,
      timeout=settings.llm_timeout
    )

  return LocalEmbedder(
    model=settings.embedding_model,
    query_prefix=settings.embedding_query_prefix,
    document_prefix=settings.embedding_document_prefix
  )

__all__ = ["Embedder", "get_embedder"]
