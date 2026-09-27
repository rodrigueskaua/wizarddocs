from services.pdf_service import build_chunks, split_text_into_chunks

TEXT = " ".join(f"palavra{i}" for i in range(400))


def test_nao_corta_palavras_no_meio():
  words = set(TEXT.split())

  for chunk in split_text_into_chunks(TEXT, chunk_size=100, overlap=20):
    assert set(chunk.split()) <= words


def test_respeita_tamanho_maximo():
  for chunk in split_text_into_chunks(TEXT, chunk_size=100, overlap=20):
    assert len(chunk) <= 100


def test_chunks_consecutivos_se_sobrepoem():
  chunks = split_text_into_chunks(TEXT, chunk_size=100, overlap=20)

  for previous, current in zip(chunks, chunks[1:]):
    assert current.split()[0] in previous.split()


def test_cobre_o_texto_inteiro():
  chunks = split_text_into_chunks(TEXT, chunk_size=100, overlap=20)

  assert chunks[0].startswith("palavra0 ")
  assert chunks[-1].endswith("palavra399")


def test_texto_vazio_nao_gera_chunks():
  assert split_text_into_chunks("   \n ") == []


def test_trecho_nunca_mistura_paginas():
  pages = [(1, "fim da página um"), (3, "começo da página três")]

  assert build_chunks(pages, chunk_size=1000, overlap=100) == [
    {"text": "fim da página um", "page": 1},
    {"text": "começo da página três", "page": 3},
  ]
