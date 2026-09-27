from typing import Protocol

class LLMError(Exception):
  pass

class LLMNotConfiguredError(LLMError):
  pass

class LLMProvider(Protocol):
  name: str
  model: str

  def generate(self, system: str, prompt: str, max_tokens: int = 2048) -> str: ...
