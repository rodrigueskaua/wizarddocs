import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.pdf import router as pdf_router
from api.query import router as query_router
from core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title="WizardDocs API",
    description="Perguntas e respostas sobre PDFs com busca semântica (RAG), citações e múltiplos provedores de LLM.",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok"}

app.include_router(pdf_router, prefix="/api", tags=["Documentos"])
app.include_router(query_router, prefix="/api", tags=["Perguntas"])
