import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from pypdf.errors import PdfReadError

from core.config import settings
from database.chromadb import (
  delete_document, document_hash, get_document, list_documents, store_document
)
from models.schemas import DocumentList, UploadResponse
from services.embedding_service import embed_documents
from services.pdf_service import build_chunks, extract_pages, file_sha256
from services.summary_service import delete_pdf_summary, generate_summary, save_pdf_summary

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload-pdf/", status_code=status.HTTP_201_CREATED, response_model=UploadResponse)
async def upload_pdf(file: UploadFile, response: Response):
  if file.content_type != "application/pdf":
    raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")

  if file.size and file.size > settings.max_upload_mb * 1024 * 1024:
    raise HTTPException(status_code=413, detail=f"O PDF excede o limite de {settings.max_upload_mb} MB.")

  filename = file.filename or "documento.pdf"
  sha256 = await run_in_threadpool(file_sha256, file.file)

  if await run_in_threadpool(document_hash, filename) == sha256:
    existing = await run_in_threadpool(get_document, filename)
    response.status_code = status.HTTP_200_OK
    return UploadResponse(
      filename=filename,
      status="unchanged",
      pages=existing["pages"],
      total_chunks=existing["chunks"],
      summary=None
    )

  try:
    pages = await run_in_threadpool(extract_pages, file.file)
  except PdfReadError:
    raise HTTPException(status_code=422, detail="Não foi possível ler o PDF.")

  chunks = build_chunks(pages, settings.chunk_size, settings.chunk_overlap)
  if not chunks:
    raise HTTPException(
      status_code=422,
      detail="O PDF não contém texto extraível (PDFs escaneados precisam de OCR)."
    )

  embeddings = await run_in_threadpool(embed_documents, [chunk["text"] for chunk in chunks])
  await run_in_threadpool(store_document, filename, sha256, chunks, embeddings)

  full_text = "\n\n".join(text for _, text in pages)

  return UploadResponse(
    filename=filename,
    status="indexed",
    pages=len(pages),
    total_chunks=len(chunks),
    summary=await _summarize(filename, full_text)
  )

@router.get("/documents/", response_model=DocumentList)
async def get_documents():
  return {"documents": await run_in_threadpool(list_documents)}

@router.delete("/documents/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(filename: str):
  if await run_in_threadpool(delete_document, filename) == 0:
    raise HTTPException(status_code=404, detail="Documento não encontrado.")
  await delete_pdf_summary(filename)

async def _summarize(filename: str, text: str) -> Optional[str]:
  """O resumo é um extra: se falhar, o PDF continua indexado e o upload não quebra."""
  try:
    summary = await run_in_threadpool(generate_summary, text)
    if summary:
      await save_pdf_summary(filename, summary)
    return summary
  except Exception:
    logger.exception("Falha ao gerar ou salvar o resumo de %s", filename)
    return None
