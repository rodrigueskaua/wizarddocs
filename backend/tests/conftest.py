import os
import tempfile

import pytest
from fpdf import FPDF

os.environ["CHROMADB_DIR"] = tempfile.mkdtemp(prefix="wizarddocs-chroma-")
os.environ["OPENAI_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["LLM_PROVIDER"] = ""
os.environ["MONGO_URI"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from core.config import settings  # noqa: E402
from database import chromadb as vector_db  # noqa: E402
from llm.gemini_provider import GeminiProvider  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture
def client():
  for collection in vector_db.client.list_collections():
    vector_db.client.delete_collection(getattr(collection, "name", collection))
  return TestClient(app)


class FakeLLM:
  def __init__(self):
    self.calls = []
    self.replies = []

  def reply(self, *texts):
    self.replies.extend(texts)

  def generate(self, system, prompt):
    self.calls.append({"system": system, "prompt": prompt})
    reply = self.replies.pop(0) if self.replies else "resposta [1]"
    if isinstance(reply, Exception):
      raise reply
    return reply


@pytest.fixture
def fake_llm(monkeypatch):
  fake = FakeLLM()
  monkeypatch.setattr(settings, "gemini_api_key", "chave-de-teste")
  monkeypatch.setattr(
    GeminiProvider, "generate", lambda self, system, prompt, max_tokens=2048: fake.generate(system, prompt)
  )
  return fake


def make_pdf(*pages: list[str]) -> bytes:
  pdf = FPDF()
  pdf.set_font("Helvetica", size=11)
  for paragraphs in pages:
    pdf.add_page()
    for paragraph in paragraphs:
      pdf.multi_cell(0, 6, paragraph)
      pdf.ln(2)
  return bytes(pdf.output())


FERIAS = [
  "Política de férias da empresa Alfa.",
  "O colaborador tem direito a 30 dias de férias após 12 meses de trabalho, "
  "podendo dividir em até três períodos, sendo que um deles não pode ser inferior a 14 dias.",
]

REEMBOLSO = [
  "Manual de reembolso de despesas.",
  "Despesas com táxi são reembolsadas em até 5 dias úteis mediante apresentação de nota fiscal.",
]

BENEFICIOS = [
  "Benefícios.",
  "A empresa fornece vale-refeição de R$ 40 por dia útil trabalhado.",
]


@pytest.fixture
def ferias_pdf() -> bytes:
  return make_pdf(FERIAS)


@pytest.fixture
def reembolso_pdf() -> bytes:
  return make_pdf(REEMBOLSO)


@pytest.fixture
def manual_pdf() -> bytes:
  return make_pdf(FERIAS, BENEFICIOS)
