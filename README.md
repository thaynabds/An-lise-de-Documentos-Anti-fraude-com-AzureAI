# An-lise-de-Documentos-Anti-fraude-com-AzureAI
implementando uma solução de análise automatizada de documentos utilizando AzureAI para identificar padrões de fraude, validar autenticidade e aumentar a segurança de transações e processos empresariais, garantindo maior confiabilidade no processamento de documentos sensíveis.  Azure OpenAI
<div align="center">

# 🔍 Análise de Documentos Anti-Fraude com Azure AI

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Azure Document Intelligence](https://img.shields.io/badge/Azure-Document%20Intelligence-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/services/form-recognizer/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interface%20Web-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Anti-Fraud](https://img.shields.io/badge/Anti--Fraude-IA%20Generativa-EF4444?style=for-the-badge&logo=shield&logoColor=white)](#)
[![DIO](https://img.shields.io/badge/DIO-Desafio%20de%20Projeto-E91E63?style=for-the-badge&logo=dio&logoColor=white)](https://dio.me/)

<br/>

> **Desafio de Projeto DIO** — Bootcamp Bradesco GenAI & Dados  
> Solução de análise automatizada de documentos com **Azure AI Document Intelligence**  
> para identificar padrões de fraude, validar autenticidade e proteger transações empresariais.

</div>

---

## 📌 Sobre o Projeto

Este sistema implementa uma **pipeline completa de detecção de fraudes em documentos** utilizando o serviço **Azure AI Document Intelligence** (anteriormente Form Recognizer). A solução combina:

- 🤖 **Modelos Predefinidos** — Análise de faturas, recibos, identidades e cartões de visita
- 🏋️ **Modelos Personalizados** — Treinamento com documentos específicos da empresa
- 🛡️ **Motor Anti-Fraude** — Regras de negócio configuráveis com score de risco 0-100
- 🌐 **Interface Web** — Dashboard interativo com Streamlit
- 📊 **Relatórios JSON** — Exportação estruturada de resultados para auditoria

---

## 🏗️ Arquitetura da Solução

```
  📄 Documento (PDF / Imagem)
         │
         ▼
  ┌─────────────────────────────────────┐
  │   Azure AI Document Intelligence    │
  │                                     │
  │  Modelos Predefinidos:              │
  │  • prebuilt-invoice  (Faturas)      │
  │  • prebuilt-receipt  (Recibos)      │
  │  • prebuilt-idDocument (Identidade) │
  │  • prebuilt-layout   (Layout OCR)   │
  │                                     │
  │  Modelos Personalizados:            │
  │  • Template  (layouts fixos)        │
  │  • Neural    (documentos mistos)    │
  │  • Composto  (múltiplos modelos)    │
  └──────────────┬──────────────────────┘
                 │  JSON com campos extraídos
                 │  + scores de confiança
                 ▼
  ┌─────────────────────────────────────┐
  │      Motor Anti-Fraude              │
  │                                     │
  │  Regras verificadas:                │
  │  ✓ Confiança do documento           │
  │  ✓ Campos obrigatórios presentes    │
  │  ✓ Confiança por campo              │
  │  ✓ Valores monetários (limites)     │
  │  ✓ Datas futuras / vencidas         │
  │  ✓ Consistência entre campos        │
  └──────────────┬──────────────────────┘
                 │
                 ▼
  📊 Relatório de Risco
  🟢 NENHUM | 🟠 BAIXO | 🟡 MÉDIO | 🔴 ALTO
```

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📄 Análise de Faturas | Extrai vendedor, data, número, itens e total |
| 🧾 Análise de Recibos | Extrai estabelecimento, data, produtos e valor |
| 🪪 Análise de Identidade | Extrai nome, documento, data de nascimento |
| 🔤 OCR Layout | Extrai todo texto e estrutura de qualquer documento |
| 🤖 Modelo Personalizado | Usa modelos treinados com documentos da empresa |
| 🛡️ Score de Risco | Pontuação 0-100 com nível: Nenhum/Baixo/Médio/Alto |
| 🚨 Alertas Inteligentes | Detecção de valores suspeitos, datas e confiança baixa |
| 📊 Relatório JSON | Exportação estruturada para auditoria e BI |
| 🌐 Interface Web | Dashboard Streamlit sem necessidade de código |

---

## 🛡️ Regras Anti-Fraude Implementadas

### Score de Risco (0 a 100 pontos)

| Regra | Pontos | Nível |
|---|---|---|
| Confiança do doc abaixo do mínimo | +30 | ⚠️ Médio |
| Campo obrigatório ausente | +20 | ⚠️ Médio |
| Campo com confiança < 60% | +10 | ⚠️ Baixo |
| Valor acima do limite configurado | +40 | 🚨 Alto |
| Valor abaixo do mínimo | +15 | ⚠️ Baixo |
| Data futura detectada | +35 | 🚨 Alto |
| Documento com mais de 1 ano | +20 | ⚠️ Médio |

### Classificação Final

| Score | Nível | Ação Recomendada |
|---|---|---|
| 0–19 | 🟢 NENHUM | Documento aprovado — prossiga normalmente |
| 20–39 | 🟠 BAIXO | Monitore e registre para auditoria futura |
| 40–69 | 🟡 MÉDIO | Solicite documentação adicional e revisão humana |
| 70–100 | 🔴 ALTO | Bloqueie e encaminhe para análise manual imediata |

---

## 📁 Estrutura do Repositório

```
antifraude-azure-ai/
│
├── 🐍 src/
│   └── antifraude.py              # Motor principal: análise + detecção de fraude
│
├── 🌐 app.py                      # Interface Web com Streamlit
│
├── 📄 exemplos/
│   └── relatorio-exemplo.json     # Exemplo de relatório gerado pelo sistema
│
├── 📋 requirements.txt            # Dependências Python
├── 🔒 .env.example                # Modelo de variáveis de ambiente
├── 🚫 .gitignore
└── 📖 README.md
```

---

## 🚀 Como Executar

### 1. Clone o repositório
```bash
git clone https://github.com/thaynabds/antifraude-azure-ai.git
cd antifraude-azure-ai
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as credenciais
```bash
cp .env.example .env
```
```env
AZURE_DOCUMENT_ENDPOINT=https://seu-recurso.cognitiveservices.azure.com/
AZURE_DOCUMENT_KEY=sua_chave_aqui
```

### 4a. Rodar via terminal
```bash
python src/antifraude.py
```

### 4b. Rodar interface web
```bash
streamlit run app.py
```

---

## 🔑 Criando o Recurso no Azure

1. Acesse o [Portal do Azure](https://portal.azure.com)
2. Clique em **Criar recurso** → busque **Document Intelligence**
3. Preencha: Grupo de Recursos, Nome, Região e Nível (F0 = gratuito)
4. Após criar, acesse **Chaves e Ponto de Extremidade**
5. Copie **Chave 1** e **Ponto de Extremidade** para o `.env`

---

## 📡 Modelos Disponíveis

### Predefinidos (sem treinamento)
| Modelo | Documento | Campos Extraídos |
|---|---|---|
| `prebuilt-invoice` | Faturas | VendorName, InvoiceDate, TotalAmount, Items... |
| `prebuilt-receipt` | Recibos | MerchantName, TransactionDate, Total, Items... |
| `prebuilt-idDocument` | Identidade | FirstName, LastName, DocumentNumber, DOB... |
| `prebuilt-businessCard` | Cartão de visita | ContactNames, Emails, Phones, Company... |
| `prebuilt-layout` | Qualquer | Texto, tabelas, estrutura por OCR |

### Personalizados (com treinamento no Document Intelligence Studio)
| Tipo | Quando Usar |
|---|---|
| **Template** | Formulários com layout fixo e previsível |
| **Neural** | Documentos de tipo misto ou variável |
| **Composto** | Conjunto de vários modelos em um único |

---

## 📊 Exemplo de Resposta da API

```json
{
  "analyzeResult": {
    "apiVersion": "2023-07-31",
    "modelId": "prebuilt-invoice",
    "pages": [{
      "pageNumber": 1,
      "width": 8.5,
      "height": 11,
      "unit": "inch"
    }],
    "documents": [{
      "docType": "invoice",
      "confidence": 0.98,
      "fields": {
        "VendorName":   { "value": "Contoso", "confidence": 0.99 },
        "InvoiceDate":  { "value": "2021-01-01", "confidence": 0.95 },
        "TotalAmount":  { "value": 3.99, "confidence": 0.97 }
      }
    }]
  }
}
```

---

## 🛠️ Tecnologias Utilizadas

- **[Python 3.9+](https://www.python.org/)** — Linguagem principal
- **[Azure AI Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)** — OCR e extração estruturada
- **[azure-ai-formrecognizer SDK](https://pypi.org/project/azure-ai-formrecognizer/)** — SDK Python para Document Intelligence
- **[Streamlit](https://streamlit.io/)** — Interface web interativa
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — Gerenciamento seguro de credenciais

---

## 📚 Referências

| Recurso | Link |
|---|---|
| 📖 Documentação Document Intelligence | [learn.microsoft.com/azure/ai-services/document-intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/) |
| 🎓 Microsoft Learn — Document Intelligence | [learn.microsoft.com/training](https://learn.microsoft.com/training/modules/analyze-receipts-form-recognizer/) |
| 🔗 Document Intelligence Studio | [documentintelligence.ai.azure.com](https://documentintelligence.ai.azure.com/) |
| 🌐 Plataforma DIO | [dio.me](https://dio.me/) |
| ☁️ Portal Azure | [portal.azure.com](https://portal.azure.com) |

---

## 👩‍💻 Autora

<div align="center">

**Thayná Batista da Silva**  
Aluna de Análise e Desenvolvimento de Sistemas  
Faculdade Senac Recife-PE · Turma 2025 · Formação prevista: 2027

</div>

---

## 📬 Contato

<div align="center">
  <a href="https://br.linkedin.com/in/thaynabds" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="https://www.instagram.com/thaynabdstec/" target="_blank">
    <img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" />
  </a>
</div>

📧 Email: [thaynabdstec@gmail.com](mailto:thaynabdstec@gmail.com)  
📱 Telefone: +55 (81) 97912-6121

<div align="center">

![Cartão TEC Thayná](https://raw.githubusercontent.com/thaynabds/AppMedSmart/refs/heads/main/Cart%C3%A3o%20TEC%20Thayn%C3%A1%20Batista%20da%20Silva.png)

</div>

---

<div align="center">

Feito com 💜 por **Thayná Batista da Silva** durante o Bootcamp da **DIO**

</div>
