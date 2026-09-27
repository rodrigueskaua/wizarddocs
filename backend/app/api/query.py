import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from core.config import settings
from llm import LLMError, LLMNotConfiguredError, configured_providers, default_provider, get_provider
from models.schemas import ProvidersResponse, QueryRequest, QueryResponse
from services.query_service import query_knowledge_base

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/query/", response_model=QueryResponse)
async def query_pdf_data(body: QueryRequest):
  provider = body.provider or default_provider() or "local"

  try:
    return await run_in_threadpool(
      query_knowledge_base,
      body.question,
      provider,
      body.top_k,
      body.source,
      [message.model_dump() for message in body.history]
    )
  except LLMNotConfiguredError:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail=f"O provedor '{provider}' não está configurado. Veja GET /api/providers/."
    )
  except LLMError:
    logger.exception("Falha no provedor %s", provider)
    raise HTTPException(
      status_code=status.HTTP_502_BAD_GATEWAY,
      detail=f"Falha ao consultar o provedor '{provider}'. Tente novamente ou use outro provedor."
    )
  except Exception:
    logger.exception("Falha ao responder a pergunta")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Erro interno ao processar a pergunta."
    )

@router.get("/providers/", response_model=ProvidersResponse)
async def list_providers():
  embedding_model = (
    settings.gemini_embedding_model if settings.embedding_provider == "gemini" else settings.embedding_model
  )
  return {
    "default": default_provider() or "local",
    "available": [
      {"name": "local", "model": embedding_model},
      *({"name": name, "model": get_provider(name).model} for name in configured_providers())
    ],
    "embedding_provider": settings.embedding_provider,
    "embedding_model": embedding_model
  }
