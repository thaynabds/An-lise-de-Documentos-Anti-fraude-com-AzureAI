"""
🔍 Análise de Documentos Anti-fraude com Azure AI Document Intelligence
Desafio de Projeto DIO — Bootcamp Bradesco GenAI & Dados
Autora: Thayná Batista da Silva
Curso: Análise e Desenvolvimento de Sistemas — Faculdade Senac Recife-PE
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── CONFIGURAÇÃO ──────────────────────────────────────────────────────────────
ENDPOINT  = os.getenv("AZURE_DOCUMENT_ENDPOINT")
API_KEY   = os.getenv("AZURE_DOCUMENT_KEY")
API_VER   = "2023-07-31"

try:
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_SDK = True
except ImportError:
    AZURE_SDK = False

import requests


# ── REGRAS DE DETECÇÃO DE FRAUDE ──────────────────────────────────────────────
REGRAS_FRAUDE = {
    "fatura": {
        "valor_maximo":        50_000.00,
        "valor_minimo":            10.00,
        "dias_vencimento_max":       90,
        "campos_obrigatorios": ["VendorName", "InvoiceDate", "TotalAmount"],
        "confianca_minima":          0.75,
    },
    "recibo": {
        "valor_maximo":        10_000.00,
        "confianca_minima":          0.70,
        "campos_obrigatorios": ["MerchantName", "TransactionDate", "Total"],
    },
    "identidade": {
        "confianca_minima":          0.85,
        "campos_obrigatorios": ["FirstName", "LastName", "DocumentNumber"],
    },
}


# ── CLIENTE AZURE ─────────────────────────────────────────────────────────────
def get_client():
    if not AZURE_SDK:
        raise RuntimeError("SDK não instalado. Execute: pip install azure-ai-formrecognizer")
    if not ENDPOINT or not API_KEY:
        raise RuntimeError("Configure AZURE_DOCUMENT_ENDPOINT e AZURE_DOCUMENT_KEY no .env")
    return DocumentAnalysisClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(API_KEY),
    )


# ── ANÁLISE DE DOCUMENTOS ─────────────────────────────────────────────────────

def analisar_fatura(url_ou_caminho: str) -> dict:
    """Analisa fatura usando modelo predefinido prebuilt-invoice."""
    client = get_client()
    print("📄 Analisando fatura...")

    if url_ou_caminho.startswith("http"):
        poller = client.begin_analyze_document_from_url("prebuilt-invoice", url_ou_caminho)
    else:
        with open(url_ou_caminho, "rb") as f:
            poller = client.begin_analyze_document("prebuilt-invoice", f)

    result = poller.result()
    faturas = []

    for doc in result.documents:
        campos = {}
        for nome, campo in doc.fields.items():
            if campo:
                campos[nome] = {
                    "valor":      campo.value,
                    "confianca":  round(campo.confidence or 0, 4),
                    "conteudo":   campo.content,
                }
        faturas.append({
            "tipo":          doc.doc_type,
            "confianca_doc": round(doc.confidence or 0, 4),
            "campos":        campos,
        })

    return {"modelo": "prebuilt-invoice", "documentos": faturas}


def analisar_recibo(url_ou_caminho: str) -> dict:
    """Analisa recibo usando modelo predefinido prebuilt-receipt."""
    client = get_client()
    print("🧾 Analisando recibo...")

    if url_ou_caminho.startswith("http"):
        poller = client.begin_analyze_document_from_url("prebuilt-receipt", url_ou_caminho)
    else:
        with open(url_ou_caminho, "rb") as f:
            poller = client.begin_analyze_document("prebuilt-receipt", f)

    result = poller.result()
    recibos = []

    for doc in result.documents:
        campos = {}
        for nome, campo in doc.fields.items():
            if campo:
                campos[nome] = {
                    "valor":     campo.value,
                    "confianca": round(campo.confidence or 0, 4),
                }
        recibos.append({
            "tipo":          doc.doc_type,
            "confianca_doc": round(doc.confidence or 0, 4),
            "campos":        campos,
        })

    return {"modelo": "prebuilt-receipt", "documentos": recibos}


def analisar_identidade(url_ou_caminho: str) -> dict:
    """Analisa documento de identidade usando modelo prebuilt-idDocument."""
    client = get_client()
    print("🪪 Analisando documento de identidade...")

    if url_ou_caminho.startswith("http"):
        poller = client.begin_analyze_document_from_url("prebuilt-idDocument", url_ou_caminho)
    else:
        with open(url_ou_caminho, "rb") as f:
            poller = client.begin_analyze_document("prebuilt-idDocument", f)

    result = poller.result()
    identidades = []

    for doc in result.documents:
        campos = {}
        for nome, campo in doc.fields.items():
            if campo:
                campos[nome] = {
                    "valor":     campo.value,
                    "confianca": round(campo.confidence or 0, 4),
                }
        identidades.append({
            "tipo":          doc.doc_type,
            "confianca_doc": round(doc.confidence or 0, 4),
            "campos":        campos,
        })

    return {"modelo": "prebuilt-idDocument", "documentos": identidades}


def analisar_modelo_personalizado(url_ou_caminho: str, model_id: str) -> dict:
    """Analisa documento usando modelo personalizado treinado."""
    client = get_client()
    print(f"🤖 Analisando com modelo personalizado: {model_id}...")

    if url_ou_caminho.startswith("http"):
        poller = client.begin_analyze_document_from_url(model_id, url_ou_caminho)
    else:
        with open(url_ou_caminho, "rb") as f:
            poller = client.begin_analyze_document(model_id, f)

    result = poller.result()
    docs = []

    for doc in result.documents:
        campos = {}
        for nome, campo in doc.fields.items():
            if campo:
                campos[nome] = {
                    "valor":     campo.value,
                    "confianca": round(campo.confidence or 0, 4),
                }
        docs.append({
            "tipo":          doc.doc_type,
            "confianca_doc": round(doc.confidence or 0, 4),
            "campos":        campos,
        })

    return {"modelo": model_id, "documentos": docs}


# ── MOTOR DE DETECÇÃO DE FRAUDE ───────────────────────────────────────────────

def detectar_fraude(analise: dict, tipo_doc: str) -> dict:
    """
    Aplica regras de negócio para detectar possíveis fraudes.

    Retorna um relatório com: score de risco, alertas e recomendação.
    """
    regras   = REGRAS_FRAUDE.get(tipo_doc, {})
    alertas  = []
    score    = 0          # 0-100 (quanto maior, mais suspeito)
    detalhes = []

    for doc in analise.get("documentos", []):
        campos        = doc.get("campos", {})
        confianca_doc = doc.get("confianca_doc", 1.0)

        # ── 1. Confiança geral do documento ───────────────────────────────────
        conf_min = regras.get("confianca_minima", 0.70)
        if confianca_doc < conf_min:
            score += 30
            alertas.append(
                f"⚠️ Confiança do documento ({confianca_doc:.0%}) abaixo do mínimo ({conf_min:.0%})"
            )

        # ── 2. Campos obrigatórios ausentes ───────────────────────────────────
        for campo in regras.get("campos_obrigatorios", []):
            if campo not in campos:
                score += 20
                alertas.append(f"❌ Campo obrigatório ausente: {campo}")

        # ── 3. Campos com baixa confiança ─────────────────────────────────────
        for nome, info in campos.items():
            conf = info.get("confianca", 1.0)
            if conf < 0.60:
                score += 10
                alertas.append(f"⚠️ Campo '{nome}' com baixa confiança: {conf:.0%}")

        # ── 4. Validação de valores monetários ────────────────────────────────
        for campo_val in ["TotalAmount", "Total", "InvoiceTotal"]:
            if campo_val in campos:
                try:
                    valor = float(str(campos[campo_val]["valor"]).replace("R$", "").replace(",", ".").strip())
                    v_max = regras.get("valor_maximo", float("inf"))
                    v_min = regras.get("valor_minimo", 0)
                    if valor > v_max:
                        score += 40
                        alertas.append(f"🚨 Valor R$ {valor:,.2f} ACIMA do limite R$ {v_max:,.2f}")
                    if valor < v_min:
                        score += 15
                        alertas.append(f"⚠️ Valor R$ {valor:,.2f} abaixo do mínimo R$ {v_min:,.2f}")
                    detalhes.append(f"Valor detectado: R$ {valor:,.2f}")
                except (ValueError, TypeError):
                    pass

        # ── 5. Validação de datas ──────────────────────────────────────────────
        for campo_data in ["InvoiceDate", "TransactionDate", "IssueDate"]:
            if campo_data in campos:
                try:
                    data = campos[campo_data]["valor"]
                    if isinstance(data, datetime):
                        dias = (datetime.now() - data).days
                        if dias < 0:
                            score += 35
                            alertas.append(f"🚨 Data FUTURA detectada: {data.strftime('%d/%m/%Y')}")
                        elif dias > 365:
                            score += 20
                            alertas.append(f"⚠️ Documento com mais de 1 ano: {data.strftime('%d/%m/%Y')}")
                        detalhes.append(f"Data: {data.strftime('%d/%m/%Y')} ({dias} dias atrás)")
                except Exception:
                    pass

    # ── Classificação final de risco ──────────────────────────────────────────
    score = min(score, 100)

    if score >= 70:
        nivel_risco    = "🔴 ALTO"
        recomendacao   = "Bloqueie o documento e encaminhe para análise manual imediata."
    elif score >= 40:
        nivel_risco    = "🟡 MÉDIO"
        recomendacao   = "Solicite documentação adicional e revisão humana."
    elif score >= 20:
        nivel_risco    = "🟠 BAIXO"
        recomendacao   = "Monitore e registre o documento para auditoria futura."
    else:
        nivel_risco    = "🟢 NENHUM"
        recomendacao   = "Documento aprovado — prossiga normalmente."

    return {
        "score_risco":   score,
        "nivel_risco":   nivel_risco,
        "alertas":       alertas,
        "detalhes":      detalhes,
        "recomendacao":  recomendacao,
        "timestamp":     datetime.now().isoformat(),
    }


# ── RELATÓRIO FINAL ───────────────────────────────────────────────────────────

def gerar_relatorio(analise: dict, fraude: dict, tipo_doc: str) -> dict:
    """Consolida análise + detecção em um relatório completo."""
    relatorio = {
        "metadata": {
            "tipo_documento": tipo_doc,
            "modelo_usado":   analise.get("modelo"),
            "timestamp":      fraude["timestamp"],
            "sistema":        "Azure AI Document Intelligence — Anti-Fraude",
        },
        "analise_documento": analise,
        "resultado_antifraude": fraude,
    }
    return relatorio


def salvar_relatorio(relatorio: dict, arquivo: str = "relatorio_antifraude.json") -> None:
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n💾 Relatório salvo em '{arquivo}'")


def exibir_relatorio(relatorio: dict) -> None:
    """Exibe o relatório formatado no terminal."""
    meta   = relatorio["metadata"]
    fraude = relatorio["resultado_antifraude"]

    print("\n" + "═" * 60)
    print("  🔍  RELATÓRIO DE ANÁLISE ANTI-FRAUDE")
    print("  Azure AI Document Intelligence")
    print("═" * 60)
    print(f"  Tipo:      {meta['tipo_documento'].upper()}")
    print(f"  Modelo:    {meta['modelo_usado']}")
    print(f"  Data/Hora: {meta['timestamp']}")
    print("─" * 60)
    print(f"  Score de Risco: {fraude['score_risco']}/100")
    print(f"  Nível de Risco: {fraude['nivel_risco']}")
    print("─" * 60)

    if fraude["alertas"]:
        print("\n  🚨 ALERTAS DETECTADOS:")
        for alerta in fraude["alertas"]:
            print(f"     {alerta}")

    if fraude["detalhes"]:
        print("\n  📋 DETALHES EXTRAÍDOS:")
        for det in fraude["detalhes"]:
            print(f"     • {det}")

    print(f"\n  💡 RECOMENDAÇÃO:\n     {fraude['recomendacao']}")
    print("═" * 60)


# ── DEMO SEM API ──────────────────────────────────────────────────────────────

def demo_sem_api():
    """Demonstração do sistema sem necessidade de credenciais Azure."""
    print("\n⚠️  Modo DEMO — Credenciais Azure não configuradas\n")

    # Simula resposta de análise de fatura
    analise_demo = {
        "modelo": "prebuilt-invoice",
        "documentos": [{
            "tipo": "invoice",
            "confianca_doc": 0.62,   # baixa confiança → dispara alerta
            "campos": {
                "VendorName":    {"valor": "Empresa XYZ LTDA", "confianca": 0.91, "conteudo": "Empresa XYZ LTDA"},
                "InvoiceDate":   {"valor": datetime(2024, 1, 15), "confianca": 0.88, "conteudo": "15/01/2024"},
                "InvoiceNumber": {"valor": "NF-000123", "confianca": 0.55, "conteudo": "NF-000123"},  # baixa conf
                "TotalAmount":   {"valor": 75000.00, "confianca": 0.90, "conteudo": "R$ 75.000,00"},  # acima limite
            },
        }]
    }

    fraude = detectar_fraude(analise_demo, "fatura")
    relatorio = gerar_relatorio(analise_demo, fraude, "fatura")
    exibir_relatorio(relatorio)
    salvar_relatorio(relatorio, "demo_relatorio_antifraude.json")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("═" * 60)
    print("  🔍  SISTEMA ANTI-FRAUDE — AZURE AI DOCUMENT INTELLIGENCE")
    print("  Desafio DIO · Thayná Batista da Silva · Senac Recife")
    print("═" * 60)

    if not ENDPOINT or not API_KEY:
        demo_sem_api()
        return

    # Exemplo de uso real — substitua pela URL ou caminho do seu documento
    url_fatura = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf"

    try:
        print("\n1️⃣  Analisando documento com Azure AI...")
        analise = analisar_fatura(url_fatura)

        print("2️⃣  Aplicando regras anti-fraude...")
        fraude = detectar_fraude(analise, "fatura")

        print("3️⃣  Gerando relatório...")
        relatorio = gerar_relatorio(analise, fraude, "fatura")

        exibir_relatorio(relatorio)
        salvar_relatorio(relatorio)

    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
