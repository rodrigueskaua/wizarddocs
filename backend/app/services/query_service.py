import re
from typing import Optional

from core.config import settings
from database.chromadb import retrieve_relevant_chunks
from llm import LLMProvider, get_provider
from services.embedding_service import embed_query
from services.prompts import (
  ANSWER_SYSTEM, CONDENSE_SYSTEM, NOT_FOUND_ANSWER, answer_prompt, condense_prompt
)

CITATION_MARKER = re.compile(r"\[(\d+)\]")
MAX_HISTORY_MESSAGES = 6

def query_knowledge_base(
  question: str,
  provider: str = "local",
  top_k: int = 5,
  source: Optional[str] = None,
  history: Optional[list[dict]] = None
) -> dict:
  llm = None if provider == "local" else get_provider(provider)
  history = (history or [])[-MAX_HISTORY_MESSAGES:]

  search_query = _condense(llm, question, history) if llm and history else question
  retrieved = retrieve_relevant_chunks(embed_query(search_query), top_k=top_k, source=source)
  relevant = [chunk for chunk in retrieved if chunk["distance"] <= settings.max_distance]

  if llm is None:
    answer = "\n\n".join(chunk["text"] for chunk in relevant) or NOT_FOUND_ANSWER
    citations = [{"index": i, **chunk} for i, chunk in enumerate(relevant, start=1)]
  elif not relevant:
    answer, citations = NOT_FOUND_ANSWER, []
  else:
    answer = llm.generate(ANSWER_SYSTEM, answer_prompt(search_query, relevant))
    citations = _cited_chunks(answer, relevant)

  return {
    "answer": answer,
    "grounded": bool(citations),
    "provider": provider,
    "model": llm.model if llm else None,
    "search_query": search_query,
    "citations": citations,
    "retrieved_chunks": [
      {**chunk, "relevant": chunk["distance"] <= settings.max_distance} for chunk in retrieved
    ]
  }

def _condense(llm: LLMProvider, question: str, history: list[dict]) -> str:
  return llm.generate(CONDENSE_SYSTEM, condense_prompt(question, history), max_tokens=256)

def _cited_chunks(answer: str, chunks: list[dict]) -> list[dict]:
  """Só os trechos que o modelo realmente citou com [n] viram citação."""
  used = sorted({
    int(number) for number in CITATION_MARKER.findall(answer) if 1 <= int(number) <= len(chunks)
  })
  return [{"index": number, **chunks[number - 1]} for number in used]
