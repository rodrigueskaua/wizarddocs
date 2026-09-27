import os
from dotenv import load_dotenv

load_dotenv()

def _e5_prompt_prefix(model: str, prefix: str) -> str:
  return prefix if "e5" in model.lower() else ""

class Settings:
  def __init__(self):
    self.env = os.getenv("APP_ENV", "development")
    self.app_port = int(os.getenv("APP_PORT", 8000))
    self.chromadb_dir = os.getenv("CHROMADB_DIR", "./chroma_db")
    self.mongo_uri = os.getenv("MONGO_URI", "")
    self.max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", 20))
    self.cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]

    self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local")
    self.embedding_model = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    self.embedding_query_prefix = os.getenv("EMBEDDING_QUERY_PREFIX", _e5_prompt_prefix(self.embedding_model, "query: "))
    self.embedding_document_prefix = os.getenv("EMBEDDING_DOCUMENT_PREFIX", _e5_prompt_prefix(self.embedding_model, "passage: "))
    self.gemini_embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    self.embedding_dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", 768))
    self.chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
    self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 150))
    self.max_distance = float(os.getenv("MAX_DISTANCE", 0.20))

    self.llm_provider = os.getenv("LLM_PROVIDER", "")
    self.llm_timeout = float(os.getenv("LLM_TIMEOUT", 60))
    self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    self.openai_model = os.getenv("OPENAI_MODEL", "gpt-6-luna")
    self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

settings = Settings()
