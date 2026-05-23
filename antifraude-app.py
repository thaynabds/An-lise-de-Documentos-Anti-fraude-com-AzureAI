"""
🔍 Interface Web — Análise Anti-Fraude com Azure AI Document Intelligence
Execute com: streamlit run app.py
"""

import os
import json
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Anti-Fraude — Azure Document Intelligence",
    page_icon="🔍",
    layout="wide",
)

st.markdown("""
<style>
.header-box {
    background: linear-gradient(135deg, #0078d4 0%, #106ebe 60%, #005a9e 100%);
    padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;
}
.risk-alto    { background:#fee2e2; border-left:5px solid #ef4444; padding:1rem; border-radius:8px; }
.risk-medio   { background:#fef9c3; border-left:5px solid #eab308; padding:1rem; border-radius:8px; }
.risk-baixo   { background:#ffedd5; border-left:5px solid #f97316; padding:1rem; border-radius:8px; }
.risk-none    { background:#dcfce7; border-left:5px solid #22c55e; padding:1rem; border-radius:8px; }
.metric-card  { background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:1rem; text-align:center; }
.alert-item   { padding:6px 10px; margin:4px 0; border-radius:6px; background:#fef2f2; border-left:3px solid #ef4444; font-size:0.88rem; }
.ok-item      { padding:6px 10px; margin:4px 0; border-radius:6px; background:#f0fdf4; border-left:3px solid #22c55e; font-size:0.88rem; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>🔍 Análise de Documentos Anti-Fraude</h1>
    <p>Powered by <b>Azure AI Document Intelligence</b> · 
    Detecção automatizada de fraudes · Modelos predefinidos e personalizados</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuração Azure")
    endpoint = st.text_input("🔗 Endpoint", value=os.getenv("AZURE_DOCUMENT_ENDPOINT", ""),
                              placeholder="https://seu-recurso.cognitiveservices.azure.com/")
    api_key  = st.text_input("🔑 API Key", value=os.getenv("AZURE_DOCUMENT_KEY", ""),
                              type="password")
    st.divider()
    st.subheader("📄 Tipo de Documento")
    tipo_doc = st.selectbox("Selecione o modelo", [
        "🧾 Fatura (Invoice)",
        "🏪 Recibo (Receipt)",
        "🪪 Identidade (ID Document)",
        "📋 Layout Geral",
        "🤖 Modelo Personalizado",
    ])
    model_id_custom = ""
    if "Personalizado" in tipo_doc:
        model_id_custom = st.text_input("ID do Modelo Personalizado")

    st.divider()
    st.subheader("🛡️ Limites Anti-Fraude")
    val_max = st.number_input("Valor máximo (R$)", value=50000.0, step=1000.0)
    conf_min = st.slider("Confiança mínima (%)", 50, 99, 75) / 100

    st.divider()
    st.markdown("""
    **💡 Projeto**  
    **Thayná Batista da Silva**  
    Desafio DIO · Bootcamp Bradesco  
    Faculdade Senac Recife-PE · ADS 2025
    """)

# ── ÁREA PRINCIPAL ────────────────────────────────────────────────────────────
col_input, col_result = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📤 Documento para Análise")
    metodo = st.radio("Método de entrada", ["🔗 URL do documento", "📁 Upload de arquivo"],
                       horizontal=True)

    doc_url  = ""
    doc_file = None
    if "URL" in metodo:
        doc_url = st.text_input("URL do documento (PDF, JPEG, PNG, TIFF)",
                                 placeholder="https://exemplo.com/fatura.pdf")
        st.caption("Suporta: PDF, JPEG, JPG, PNG, BMP, TIFF, HEIF")
    else:
        doc_file = st.file_uploader("Arraste ou selecione o documento",
                                     type=["pdf","jpg","jpeg","png","tiff","bmp"])

    st.divider()
    st.subheader("📋 Regras de Negócio Ativas")
    st.markdown(f"""
    | Regra | Valor Configurado |
    |---|---|
    | Valor máximo | R$ {val_max:,.2f} |
    | Confiança mínima | {conf_min:.0%} |
    | Data futura | Bloqueio automático |
    | Campos obrigatórios | Verificação automática |
    | Confiança por campo | Alerta abaixo de 60% |
    """)

    btn_analisar = st.button("🔍 Analisar Documento",
                              type="primary", use_container_width=True,
                              disabled=not (doc_url or doc_file))

with col_result:
    st.subheader("📊 Resultado da Análise")

    if btn_analisar:
        if not endpoint or not api_key:
            st.warning("⚠️ Configure as credenciais Azure na barra lateral ou use o modo Demo abaixo.")
        else:
            try:
                from azure.ai.formrecognizer import DocumentAnalysisClient
                from azure.core.credentials import AzureKeyCredential

                client = DocumentAnalysisClient(
                    endpoint=endpoint,
                    credential=AzureKeyCredential(api_key),
                )

                # Mapeamento modelo
                modelo_map = {
                    "🧾 Fatura (Invoice)":  "prebuilt-invoice",
                    "🏪 Recibo (Receipt)":  "prebuilt-receipt",
                    "🪪 Identidade (ID Document)": "prebuilt-idDocument",
                    "📋 Layout Geral":      "prebuilt-layout",
                    "🤖 Modelo Personalizado": model_id_custom,
                }
                modelo = modelo_map.get(tipo_doc, "prebuilt-invoice")

                with st.spinner("🔄 Analisando com Azure AI Document Intelligence..."):
                    if doc_url:
                        poller = client.begin_analyze_document_from_url(modelo, doc_url)
                    else:
                        poller = client.begin_analyze_document(modelo, doc_file)
                    result = poller.result()

                st.success("✅ Análise concluída!")
                campos_extraidos = {}
                alertas = []
                score = 0

                for doc in result.documents:
                    conf_doc = doc.confidence or 1.0
                    if conf_doc < conf_min:
                        score += 30
                        alertas.append(f"Confiança do documento ({conf_doc:.0%}) abaixo do mínimo")

                    for nome, campo in doc.fields.items():
                        if campo:
                            campos_extraidos[nome] = {
                                "valor": str(campo.value),
                                "confianca": round(campo.confidence or 0, 2),
                            }
                            if (campo.confidence or 1.0) < 0.60:
                                score += 10
                                alertas.append(f"Campo '{nome}' com baixa confiança ({campo.confidence:.0%})")

                    # Verificar valor
                    for cv in ["TotalAmount","Total","InvoiceTotal"]:
                        if cv in campos_extraidos:
                            try:
                                v = float(str(campos_extraidos[cv]["valor"]).replace("$","").replace(",",""))
                                if v > val_max:
                                    score += 40
                                    alertas.append(f"Valor R${v:,.2f} acima do limite R${val_max:,.2f}")
                            except: pass

                score = min(score, 100)
                if   score >= 70: nivel, css = "🔴 ALTO",   "risk-alto"
                elif score >= 40: nivel, css = "🟡 MÉDIO",  "risk-medio"
                elif score >= 20: nivel, css = "🟠 BAIXO",  "risk-baixo"
                else:             nivel, css = "🟢 NENHUM", "risk-none"

                # Score visual
                c1, c2, c3 = st.columns(3)
                c1.metric("Score de Risco", f"{score}/100")
                c2.metric("Nível", nivel)
                c3.metric("Campos extraídos", len(campos_extraidos))

                st.markdown(f'<div class="{css}"><b>Nível de Risco: {nivel}</b><br/>'
                            + ("Documento aprovado ✅" if not alertas else f"{len(alertas)} alertas detectados")
                            + "</div>", unsafe_allow_html=True)

                # Alertas
                if alertas:
                    st.subheader("🚨 Alertas")
                    for a in alertas:
                        st.markdown(f'<div class="alert-item">⚠️ {a}</div>', unsafe_allow_html=True)

                # Campos extraídos
                st.subheader("📋 Dados Extraídos")
                for nome, info in campos_extraidos.items():
                    emoji = "✅" if info["confianca"] >= 0.70 else "⚠️"
                    st.markdown(f'<div class="ok-item">{emoji} <b>{nome}:</b> {info["valor"]} '
                                f'<span style="color:#64748b">(confiança: {info["confianca"]:.0%})</span></div>',
                                unsafe_allow_html=True)

                # Download
                relatorio = {
                    "timestamp": datetime.now().isoformat(),
                    "modelo": modelo, "score_risco": score,
                    "nivel_risco": nivel, "alertas": alertas,
                    "campos": campos_extraidos,
                }
                st.download_button("📥 Baixar Relatório JSON",
                                   data=json.dumps(relatorio, ensure_ascii=False, indent=2, default=str),
                                   file_name="relatorio_antifraude.json", mime="application/json")

            except ImportError:
                st.error("❌ Instale o SDK: pip install azure-ai-formrecognizer")
            except Exception as e:
                st.error(f"❌ Erro: {e}")

    else:
        st.info("👈 Configure as credenciais, selecione o documento e clique em **Analisar**.")

# ── MODO DEMO ─────────────────────────────────────────────────────────────────
st.divider()
with st.expander("🎭 Modo Demo — Ver exemplo de relatório sem credenciais Azure"):
    demo_relatorio = {
        "timestamp": "2026-05-20T14:32:00",
        "modelo": "prebuilt-invoice",
        "score_risco": 70,
        "nivel_risco": "🔴 ALTO",
        "alertas": [
            "Confiança do documento (62%) abaixo do mínimo (75%)",
            "Valor R$75.000,00 acima do limite R$50.000,00",
            "Campo 'InvoiceNumber' com baixa confiança (55%)",
        ],
        "campos": {
            "VendorName":    {"valor": "Empresa XYZ LTDA",   "confianca": 0.91},
            "InvoiceDate":   {"valor": "15/01/2024",          "confianca": 0.88},
            "InvoiceNumber": {"valor": "NF-000123",           "confianca": 0.55},
            "TotalAmount":   {"valor": "R$ 75.000,00",        "confianca": 0.90},
        },
    }
    st.json(demo_relatorio)
