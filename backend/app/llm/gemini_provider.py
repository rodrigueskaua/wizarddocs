from google import genai
from google.genai import errors, types

from llm.base import LLMError

class GeminiProvider:
  name = "gemini"

  def __init__(self, api_key: str, model: str, timeout: float):
    self.model = model
    self._client = genai.Client(
      api_key=api_key,
      http_options=types.HttpOptions(
        timeout=int(timeout * 1000),
        retry_options=types.HttpRetryOptions(attempts=3)
      )
    )

  def generate(self, system: str, prompt: str, max_tokens: int = 2048) -> str:
    try:
      response = self._client.models.generate_content(
        model=self.model,
        contents=prompt,
        config=types.GenerateContentConfig(
          system_instruction=system,
          max_output_tokens=max_tokens,
          temperature=0.2
        )
      )
    except errors.APIError as error:
      raise LLMError(f"Gemini ({self.model}): {error}") from error

    text = (response.text or "").strip()
    if not text:
      raise LLMError(f"Gemini ({self.model}) devolveu uma resposta vazia.")
    return text
