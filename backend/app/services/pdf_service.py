import hashlib

from pypdf import PdfReader

def file_sha256(pdf_file) -> str:
  digest = hashlib.sha256()
  for block in iter(lambda: pdf_file.read(1024 * 1024), b""):
    digest.update(block)
  pdf_file.seek(0)
  return digest.hexdigest()

def extract_pages(pdf_file) -> list[tuple[int, str]]:
  """Devolve (número da página, texto) de cada página que tem texto extraível."""
  reader = PdfReader(pdf_file)
  pages = []

  for number, page in enumerate(reader.pages, start=1):
    text = (page.extract_text() or "").strip()
    if text:
      pages.append((number, text))

  return pages

def build_chunks(pages: list[tuple[int, str]], chunk_size: int, overlap: int) -> list[dict]:
  """Divide cada página separadamente, para que todo trecho aponte para uma única página."""
  return [
    {"text": text, "page": number}
    for number, page_text in pages
    for text in split_text_into_chunks(page_text, chunk_size, overlap)
  ]

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
  """Divide o texto em trechos de até chunk_size caracteres, sempre cortando entre palavras.

  Cada trecho começa repetindo as últimas palavras do anterior (até overlap caracteres),
  para que uma frase dividida na fronteira ainda apareça inteira em algum trecho.
  """
  chunks = []
  current = []

  for word in text.split():
    if current and len(" ".join(current + [word])) > chunk_size:
      chunks.append(" ".join(current))
      current = _overlap_tail(current, overlap)
    current.append(word)

  if current:
    chunks.append(" ".join(current))

  return chunks

def _overlap_tail(words: list[str], overlap: int) -> list[str]:
  tail = []
  for word in reversed(words):
    if len(" ".join([word] + tail)) > overlap:
      break
    tail.insert(0, word)
  return tail
