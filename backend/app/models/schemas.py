from typing import Literal, Optional

from pydantic import BaseModel, Field

class Message(BaseModel):
  role: Literal["user", "assistant"]
  content: str = Field(..., min_length=1)

class QueryRequest(BaseModel):
  question: str = Field(..., min_length=1, max_length=2000)
  top_k: int = Field(5, ge=1, le=20)
  provider: Optional[Literal["local", "openai", "gemini"]] = Field(
    None, description="Sem valor usa o provedor padrão (LLM_PROVIDER) ou 'local' se nenhum estiver configurado"
  )
  source: Optional[str] = Field(None, description="Restringe a busca a um arquivo enviado")
  history: list[Message] = Field(
    default_factory=list, description="Mensagens anteriores da conversa, da mais antiga para a mais recente"
  )

class RetrievedChunk(BaseModel):
  text: str
  source: str
  page: int
  chunk: int
  distance: float
  relevant: bool

class Citation(BaseModel):
  index: int
  text: str
  source: str
  page: int
  chunk: int
  distance: float

class QueryResponse(BaseModel):
  answer: str
  grounded: bool = Field(..., description="True quando a resposta cita ao menos um trecho dos documentos")
  provider: str
  model: Optional[str]
  search_query: str = Field(..., description="Pergunta usada na busca (reescrita quando há histórico)")
  citations: list[Citation]
  retrieved_chunks: list[RetrievedChunk]

class UploadResponse(BaseModel):
  filename: str
  status: Literal["indexed", "unchanged"]
  pages: int
  total_chunks: int
  summary: Optional[str]

class DocumentInfo(BaseModel):
  filename: str
  chunks: int
  pages: int

class DocumentList(BaseModel):
  documents: list[DocumentInfo]

class ProviderInfo(BaseModel):
  name: str
  model: str

class ProvidersResponse(BaseModel):
  default: str
  available: list[ProviderInfo]
  embedding_provider: str
  embedding_model: str
