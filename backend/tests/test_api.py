from conftest import make_pdf
from core.config import settings
from llm import LLMError
from services.prompts import NOT_FOUND_ANSWER


def upload(client, name, content, content_type="application/pdf"):
  return client.post("/api/upload-pdf/", files={"file": (name, content, content_type)})


def query(client, **body):
  return client.post("/api/query/", json=body)


# Upload e gestão de documentos

def test_upload_indexa_o_pdf(client, manual_pdf):
  response = upload(client, "manual.pdf", manual_pdf)

  assert response.status_code == 201
  assert response.json() == {
    "filename": "manual.pdf", "status": "indexed", "pages": 2, "total_chunks": 2, "summary": None
  }


def test_segundo_pdf_nao_sobrescreve_o_primeiro(client, ferias_pdf, reembolso_pdf):
  upload(client, "ferias.pdf", ferias_pdf)
  upload(client, "reembolso.pdf", reembolso_pdf)

  chunk = query(client, question="reembolso de táxi", top_k=1).json()["retrieved_chunks"][0]

  assert chunk["source"] == "reembolso.pdf"
  assert "táxi" in chunk["text"]


def test_reenviar_o_mesmo_arquivo_nao_reprocessa(client, ferias_pdf):
  upload(client, "ferias.pdf", ferias_pdf)

  response = upload(client, "ferias.pdf", ferias_pdf)

  assert response.status_code == 200
  assert response.json()["status"] == "unchanged"
  assert client.get("/api/documents/").json()["documents"] == [
    {"filename": "ferias.pdf", "chunks": 1, "pages": 1}
  ]


def test_nova_versao_do_arquivo_substitui_a_anterior(client, ferias_pdf, manual_pdf):
  upload(client, "politicas.pdf", ferias_pdf)

  response = upload(client, "politicas.pdf", manual_pdf)

  assert response.json()["status"] == "indexed"
  assert client.get("/api/documents/").json()["documents"] == [
    {"filename": "politicas.pdf", "chunks": 2, "pages": 2}
  ]


def test_remove_documento(client, ferias_pdf, reembolso_pdf):
  upload(client, "ferias.pdf", ferias_pdf)
  upload(client, "reembolso.pdf", reembolso_pdf)

  assert client.delete("/api/documents/ferias.pdf").status_code == 204
  assert client.delete("/api/documents/ferias.pdf").status_code == 404
  assert [d["filename"] for d in client.get("/api/documents/").json()["documents"]] == ["reembolso.pdf"]


def test_rejeita_arquivo_que_nao_e_pdf(client):
  assert upload(client, "notas.txt", b"oi", "text/plain").status_code == 400


def test_rejeita_pdf_acima_do_limite(client, ferias_pdf, monkeypatch):
  monkeypatch.setattr(settings, "max_upload_mb", 0)

  assert upload(client, "ferias.pdf", ferias_pdf).status_code == 413


def test_pdf_sem_texto_retorna_422(client):
  assert upload(client, "vazio.pdf", make_pdf([])).status_code == 422


def test_pdf_corrompido_retorna_422(client):
  assert upload(client, "quebrado.pdf", b"%PDF-1.4 lixo").status_code == 422


# Busca local (sem LLM)

def test_busca_cita_a_pagina_de_origem(client, manual_pdf):
  upload(client, "manual.pdf", manual_pdf)

  citation = query(client, question="qual o valor do vale-refeição?", top_k=1).json()["citations"][0]

  assert (citation["source"], citation["page"]) == ("manual.pdf", 2)


def test_filtra_busca_por_documento(client, ferias_pdf, reembolso_pdf):
  upload(client, "ferias.pdf", ferias_pdf)
  upload(client, "reembolso.pdf", reembolso_pdf)

  response = query(client, question="reembolso de táxi", source="ferias.pdf")

  assert {c["source"] for c in response.json()["retrieved_chunks"]} == {"ferias.pdf"}


def test_busca_com_base_vazia_nao_quebra(client):
  body = query(client, question="qualquer coisa").json()

  assert body["answer"] == NOT_FOUND_ANSWER
  assert body["grounded"] is False
  assert body["retrieved_chunks"] == []


def test_valida_corpo_da_busca(client):
  assert query(client, question="").status_code == 422
  assert query(client, question="x", top_k=0).status_code == 422
  assert query(client, question="x", provider="claude").status_code == 422
  assert query(client, question="x", history=[{"role": "system", "content": "oi"}]).status_code == 422


# Provedores de LLM

def test_provedor_nao_configurado_retorna_503(client, ferias_pdf):
  upload(client, "ferias.pdf", ferias_pdf)

  assert query(client, question="férias", provider="gemini").status_code == 503
  assert query(client, question="férias", provider="openai").status_code == 503


def test_lista_provedores(client, fake_llm):
  body = client.get("/api/providers/").json()

  assert body["default"] == "gemini"
  assert [p["name"] for p in body["available"]] == ["local", "gemini"]


def test_sem_provedor_configurado_o_padrao_e_local(client):
  assert client.get("/api/providers/").json()["default"] == "local"


def test_llm_recebe_trechos_numerados_com_origem(client, ferias_pdf, fake_llm):
  upload(client, "ferias.pdf", ferias_pdf)
  fake_llm.calls.clear()
  fake_llm.reply("São 30 dias [1].")

  body = query(client, question="quantos dias de férias?", provider="gemini").json()

  assert body["answer"] == "São 30 dias [1]."
  assert body["grounded"] is True
  assert body["model"] == settings.gemini_model
  assert "[1] (ferias.pdf, página 1)" in fake_llm.calls[0]["prompt"]
  assert "não instruções" in fake_llm.calls[0]["system"]


def test_so_trechos_citados_viram_citacao(client, manual_pdf, fake_llm):
  upload(client, "manual.pdf", manual_pdf)
  fake_llm.reply("O vale-refeição é de R$ 40 [2]. Ver também [9].")

  body = query(client, question="benefícios e férias", provider="gemini", top_k=2).json()

  assert [c["index"] for c in body["citations"]] == [2]


def test_nao_chama_o_llm_sem_trecho_relevante(client, ferias_pdf, fake_llm, monkeypatch):
  upload(client, "ferias.pdf", ferias_pdf)
  fake_llm.calls.clear()
  monkeypatch.setattr(settings, "max_distance", 0.0)

  body = query(client, question="quem ganhou a copa de 2002?", provider="gemini").json()

  assert body["answer"] == NOT_FOUND_ANSWER
  assert body["grounded"] is False
  assert fake_llm.calls == []
  assert all(not c["relevant"] for c in body["retrieved_chunks"])


def test_resposta_sem_citacao_nao_e_fundamentada(client, ferias_pdf, fake_llm):
  upload(client, "ferias.pdf", ferias_pdf)
  fake_llm.reply(NOT_FOUND_ANSWER)

  body = query(client, question="quantos dias de férias?", provider="gemini").json()

  assert body["grounded"] is False
  assert body["citations"] == []


def test_pergunta_de_acompanhamento_e_reescrita_antes_da_busca(client, ferias_pdf, fake_llm):
  upload(client, "ferias.pdf", ferias_pdf)
  fake_llm.calls.clear()
  fake_llm.reply("Em quantos períodos as férias podem ser divididas?", "Em até três [1].")

  body = query(
    client,
    question="e dá pra dividir?",
    provider="gemini",
    history=[
      {"role": "user", "content": "quantos dias de férias eu tenho?"},
      {"role": "assistant", "content": "30 dias [1]."},
    ],
  ).json()

  assert body["search_query"] == "Em quantos períodos as férias podem ser divididas?"
  assert "quantos dias de férias eu tenho?" in fake_llm.calls[0]["prompt"]
  assert "Pergunta: Em quantos períodos" in fake_llm.calls[1]["prompt"]


def test_falha_do_provedor_retorna_502_sem_vazar_detalhes(client, ferias_pdf, fake_llm):
  upload(client, "ferias.pdf", ferias_pdf)
  fake_llm.reply(LLMError("chave inválida sk-segredo"))

  response = query(client, question="férias", provider="gemini")

  assert response.status_code == 502
  assert "sk-segredo" not in response.text


# Resumo

def test_upload_gera_resumo_com_o_provedor_padrao(client, ferias_pdf, fake_llm):
  fake_llm.reply("Política de férias da empresa Alfa.")

  response = upload(client, "ferias.pdf", ferias_pdf)

  assert response.json()["summary"] == "Política de férias da empresa Alfa."


def test_falha_no_resumo_nao_derruba_o_upload(client, ferias_pdf, fake_llm):
  fake_llm.reply(LLMError("fora do ar"))

  response = upload(client, "ferias.pdf", ferias_pdf)

  assert response.status_code == 201
  assert response.json()["summary"] is None
