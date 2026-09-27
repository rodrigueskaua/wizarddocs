from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

collection = None

if settings.mongo_uri:
  client = AsyncIOMotorClient(settings.mongo_uri)
  collection = client["pdf_documents"]["summaries"]
