from types import SimpleNamespace

import httpx
import openai
import pytest
from google.genai import errors as genai_errors

from llm import LLMError
from llm.gemini_provider import GeminiProvider
from llm.openai_provider import OpenAIProvider


class Recorder:
  def __init__(self, result):
    self.result = result
    self.kwargs = None

  def __call__(self, **kwargs):
    self.kwargs = kwargs
    if isinstance(self.result, Exception):
      raise self.result
    return self.result


def openai_with(result):
  provider = OpenAIProvider(api_key="sk-teste", model="gpt-teste", timeout=5)
  create = Recorder(result)
  provider._client = SimpleNamespace(responses=SimpleNamespace(create=create))
  return provider, create


def gemini_with(result):
  provider = GeminiProvider(api_key="chave-teste", model="gemini-teste", timeout=5)
  generate_content = Recorder(result)
  provider._client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
  return provider, generate_content


def test_openai_usa_a_responses_api():
  provider, create = openai_with(SimpleNamespace(output_text="  resposta  "))

  assert provider.generate("sistema", "pergunta", max_tokens=100) == "resposta"
  assert create.kwargs == {
    "model": "gpt-teste", "instructions": "sistema", "input": "pergunta", "max_output_tokens": 100
  }


def test_openai_resposta_vazia_vira_llm_error():
  provider, _ = openai_with(SimpleNamespace(output_text=""))

  with pytest.raises(LLMError):
    provider.generate("sistema", "pergunta")


def test_openai_erro_da_api_vira_llm_error():
  error = openai.APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"))
  provider, _ = openai_with(error)

  with pytest.raises(LLMError):
    provider.generate("sistema", "pergunta")


def test_gemini_envia_instrucao_de_sistema_na_configuracao():
  provider, generate_content = gemini_with(SimpleNamespace(text=" resposta "))

  assert provider.generate("sistema", "pergunta", max_tokens=100) == "resposta"
  assert generate_content.kwargs["model"] == "gemini-teste"
  assert generate_content.kwargs["contents"] == "pergunta"
  config = generate_content.kwargs["config"]
  assert (config.system_instruction, config.max_output_tokens) == ("sistema", 100)


def test_gemini_resposta_vazia_vira_llm_error():
  provider, _ = gemini_with(SimpleNamespace(text=None))

  with pytest.raises(LLMError):
    provider.generate("sistema", "pergunta")


def test_gemini_erro_da_api_vira_llm_error():
  provider, _ = gemini_with(genai_errors.APIError(429, {"error": {"message": "quota"}}))

  with pytest.raises(LLMError):
    provider.generate("sistema", "pergunta")
