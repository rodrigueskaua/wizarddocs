from datetime import datetime
from typing import Optional

from database.mongodb import collection
from llm import default_provider, get_provider
from services.prompts import SUMMARY_SYSTEM, summary_prompt

SUMMARY_MAX_CHARS = 12000

def generate_summary(text: str) -> Optional[str]:
  provider = default_provider()
  if provider is None:
    return None
  return get_provider(provider).generate(
    SUMMARY_SYSTEM, summary_prompt(text[:SUMMARY_MAX_CHARS]), max_tokens=1024
  )

async def save_pdf_summary(filename: str, summary: str):
  if collection is None:
    return

  await collection.replace_one(
    {"filename": filename},
    {"filename": filename, "summary": summary, "uploaded_at": datetime.now()},
    upsert=True
  )

async def delete_pdf_summary(filename: str):
  if collection is not None:
    await collection.delete_one({"filename": filename})
