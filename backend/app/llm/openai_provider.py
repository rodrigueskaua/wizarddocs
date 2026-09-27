from openai import APIError, OpenAI

from llm.base import LLMError

class OpenAIProvider:
  name = "openai"

  def __init__(self, api_key: str, model: str, timeout: float):
    self.model = model
    self._client = OpenAI(api_key=api_key, timeout=timeout, max_retries=2)

  def generate(self, system: str, prompt: str, max_tokens: int = 2048) -> str:
    try:
      response = self._client.responses.create(
        model=self.model,
        instructions=system,
        input=prompt,
        max_output_tokens=max_tokens
      )
    except APIError as error:
      raise LLMError(f"OpenAI ({self.model}): {error}") from error

    text = (response.output_text or "").strip()
    if not text:
      raise LLMError(f"OpenAI ({self.model}) devolveu uma resposta vazia.")
    return text
