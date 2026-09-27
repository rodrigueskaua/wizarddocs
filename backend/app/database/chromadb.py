import re
from collections import defaultdict
from typing import Optional

import chromadb

from core.config import settings

client = chromadb.PersistentClient(path=settings.chromadb_dir)

def collection_name() -> str:
  if settings.embedding_provider == "gemini":
    identity = f"gemini-{settings.gemini_embedding_model}-{settings.embedding_dimensions}"
  else:
    identity = settings.embedding_model
  slug = re.sub(r"[^a-zA-Z0-9._-]", "-", identity)
  return f"documents-{slug}"[:512].strip("-._")

def _collection():
  return client.get_or_create_collection(
    name=collection_name(),
    configuration={"hnsw": {"space": "cosine"}},
    metadata={"embedding_provider": settings.embedding_provider},
    embedding_function=None
  )

def document_hash(source: str) -> Optional[str]:
  result = _collection().get(where={"source": source}, limit=1, include=["metadatas"])
  return result["metadatas"][0]["sha256"] if result["metadatas"] else None

def store_document(source: str, sha256: str, chunks: list[dict], embeddings: list[list[float]]):
  collection = _collection()
  collection.delete(where={"source": source})

  ids = [f"{source}::{i}" for i in range(len(chunks))]
  metadatas = [
    {"source": source, "page": chunk["page"], "chunk": i, "sha256": sha256}
    for i, chunk in enumerate(chunks)
  ]
  documents = [chunk["text"] for chunk in chunks]

  batch_size = client.get_max_batch_size()
  for start in range(0, len(chunks), batch_size):
    end = start + batch_size
    collection.add(
      ids=ids[start:end],
      documents=documents[start:end],
      embeddings=embeddings[start:end],
      metadatas=metadatas[start:end]
    )

def delete_document(source: str) -> int:
  collection = _collection()
  ids = collection.get(where={"source": source}, include=[])["ids"]
  if ids:
    collection.delete(ids=ids)
  return len(ids)

def retrieve_relevant_chunks(
  query_embedding: list[float],
  top_k: int = 5,
  source: Optional[str] = None
) -> list[dict]:
  collection = _collection()
  if collection.count() == 0:
    return []

  results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    where={"source": source} if source else None
  )

  return [
    {
      "text": document,
      "distance": round(distance, 4),
      "source": metadata["source"],
      "page": metadata["page"],
      "chunk": metadata["chunk"]
    }
    for document, distance, metadata in zip(
      results["documents"][0], results["distances"][0], results["metadatas"][0]
    )
  ]

def get_document(source: str) -> Optional[dict]:
  metadatas = _collection().get(where={"source": source}, include=["metadatas"])["metadatas"]
  documents = _summarize(metadatas)
  return documents[0] if documents else None

def list_documents() -> list[dict]:
  return _summarize(_collection().get(include=["metadatas"])["metadatas"])

def _summarize(metadatas: list[dict]) -> list[dict]:
  chunks = defaultdict(int)
  pages = defaultdict(set)
  for metadata in metadatas:
    chunks[metadata["source"]] += 1
    pages[metadata["source"]].add(metadata["page"])

  return [
    {"filename": source, "chunks": chunks[source], "pages": len(pages[source])}
    for source in sorted(chunks)
  ]
