from functools import lru_cache
from typing import Optional

from core.config import settings
from llm.base import LLMError, LLMNotConfiguredError, LLMProvider
from llm.gemini_provider import GeminiProvider
from llm.openai_provider import OpenAIProvider

_PROVIDER_CLASSES = {"openai": OpenAIProvider, "gemini": GeminiProvider}

def _credentials(name: str) -> tuple[str, str]:
  if name == "openai":
    return settings.openai_api_key, settings.openai_model
  return settings.gemini_api_key, settings.gemini_model

def configured_providers() -> list[str]:
  return [name for name in _PROVIDER_CLASSES if _credentials(name)[0]]

def default_provider() -> Optional[str]:
  available = configured_providers()
  if settings.llm_provider in available:
    return settings.llm_provider
  return available[0] if available else None

def get_provider(name: str) -> LLMProvider:
  api_key, model = _credentials(name)
  if not api_key:
    raise LLMNotConfiguredError(f"O provedor '{name}' não está configurado.")
  return _build(name, api_key, model, settings.llm_timeout)

@lru_cache
def _build(name: str, api_key: str, model: str, timeout: float) -> LLMProvider:
  return _PROVIDER_CLASSES[name](api_key=api_key, model=model, timeout=timeout)

__all__ = [
  "LLMError", "LLMNotConfiguredError", "LLMProvider",
  "configured_providers", "default_provider", "get_provider"
]
