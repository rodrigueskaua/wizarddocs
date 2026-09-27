import numpy as np
from google import genai
from google.genai import errors, types

from llm.base import LLMError

MAX_TEXTS_PER_EMBED_REQUEST = 100

class GeminiEmbedder:
  name = "gemini"

  def __init__(self, api_key: str, model: str, dimensions: int, timeout: float):
    self.model = model
    self.dimensions = dimensions
    self._client = genai.Client(
      api_key=api_key,
      http_options=types.HttpOptions(
        timeout=int(timeout * 1000),
        retry_options=types.HttpRetryOptions(attempts=5)
      )
    )

  def embed_documents(self, texts: list[str]) -> list[list[float]]:
    embeddings = []
    for start in range(0, len(texts), MAX_TEXTS_PER_EMBED_REQUEST):
      batch = texts[start:start + MAX_TEXTS_PER_EMBED_REQUEST]
      embeddings += self._embed(batch, "RETRIEVAL_DOCUMENT")
    return embeddings

  def embed_query(self, text: str) -> list[float]:
    return self._embed([text], "RETRIEVAL_QUERY")[0]

  def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
    try:
      response = self._client.models.embed_content(
        model=self.model,
        contents=texts,
        config=types.EmbedContentConfig(
          task_type=task_type,
          output_dimensionality=self.dimensions
        )
      )
    except errors.APIError as error:
      raise LLMError(f"Gemini embeddings ({self.model}): {error}") from error

    return [_l2_normalize(embedding.values) for embedding in response.embeddings]

def _l2_normalize(values: list[float]) -> list[float]:
  vector = np.array(values)
  norm = np.linalg.norm(vector)
  return (vector / norm).tolist() if norm > 0 else vector.tolist()
