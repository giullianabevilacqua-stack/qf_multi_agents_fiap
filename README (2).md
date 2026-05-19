# 💼 Quantum Finance — Consultor Financeiro Multiagente

> **MBA Data Science & Artificial Intelligence — FIAP**
> Disciplina: Intelligent Multi Agents
> Professor: Alexandre Alves

---

## 📋 Visão Geral

O **Quantum Finance** é um sistema de **IA Agêntica** construído com **Google Agent Development Kit (ADK)** e **Gemini 2.5 Flash**. Ele simula um consultor financeiro inteligente para clientes da Quantum Finance, capaz de:

- Buscar **dados macroeconômicos reais** (Selic, IPCA, CDI) via API pública do Banco Central
- Consultar **cotações e fundamentos de ações e FIIs** em tempo real via **Bolsai API** (dados oficiais B3) com fallback para **yfinance**
- Gerar **recomendações financeiras personalizadas** com base no perfil do cliente

O diferencial do sistema está na **confiabilidade**: nenhum dado financeiro é inventado pelo modelo. Toda cotação, taxa ou indicador é obrigatoriamente buscado via ferramenta (tool) antes de ser apresentado ao cliente.

---

## 🏗️ Arquitetura Multiagente

```
┌─────────────────────────────────────────────────────────────┐
│                     USUÁRIO / CLIENTE                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          🧠 LEAD ADVISOR (Agente Orquestrador)               │
│                   gemini-2.5-flash                          │
│                                                             │
│  • Coleta perfil do cliente (risco, prazo, objetivo)        │
│  • Orquestra os subagentes                                  │
│  • Consolida informações                                    │
│  • Gera Relatório de Recomendação Final                     │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────┐    ┌─────────────────────────────────┐
│  📰 MARKET ANALYST   │    │       📈 B3 DATA AGENT           │
│  gemini-2.5-flash    │    │       gemini-2.5-flash-lite      │
│                      │    │                                 │
│ • Taxa Selic (BCB)   │    │ • Cotações em tempo real        │
│ • IPCA (BCB)         │    │   via Bolsai API                │
│ • CDI (BCB)          │    │ • Indicadores fundamentalistas  │
│ • Info sobre CDB,    │    │   (P/L, P/VP, DY, ROE)         │
│   Tesouro, FIIs,     │    │ • Top FIIs por Dividend Yield  │
│   LCI, LCA           │    │ • Histórico de preços           │
│ • Perfil Investidor  │    │ • Fallback: yfinance            │
└──────────────────────┘    └─────────────────────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────┐    ┌─────────────────────────────────┐
│  🏦 API Banco Central│    │  📊 Bolsai API (B3 Oficial)     │
│  api.bcb.gov.br      │    │  + yfinance (fallback)          │
└──────────────────────┘    └─────────────────────────────────┘
```

### Agentes e Responsabilidades

| Agente | Nome Interno | Modelo | Função |
|--------|-------------|--------|--------|
| **Lead Advisor** | `lead_advisor` | `gemini-2.5-flash` | Orquestrador principal. Coleta perfil, delega e gera relatório final |
| **Market Analyst** | `market_analyst` | `gemini-2.5-flash` | Dados macro (Selic/IPCA/CDI) e explicação de produtos financeiros |
| **B3 Data Agent** | `b3_data_agent` | `gemini-2.5-flash-lite` | Cotações e fundamentos de ações/FIIs via Bolsai API |

> O Lead Advisor e o Market Analyst utilizam `gemini-2.5-flash` (modelo completo) por exigirem raciocínio mais elaborado — orquestração de subagentes e interpretação de múltiplos resultados de ferramentas. O B3 Data Agent usa `gemini-2.5-flash-lite` por executar tarefas mais diretas de busca e formatação de dados.

---

## 🛠️ Ferramentas (Tools)

### Market Analyst Tools

| Ferramenta | Fonte | Descrição |
|-----------|-------|-----------|
| `buscar_taxa_selic()` | BCB SGS série 432 | Taxa Selic Meta vigente |
| `buscar_ipca()` | BCB SGS série 13522 | IPCA acumulado 12 meses |
| `buscar_cdi()` | BCB SGS série 12 | Taxa CDI diária |
| `explicar_produto_financeiro(produto)` | Base interna | Características, riscos e tributação de CDB, Tesouro, FIIs, LCI, LCA, Poupança |
| `classificar_perfil_investidor(risco, prazo, objetivo)` | Lógica interna | Perfil Conservador/Moderado/Arrojado + alocação sugerida |

### B3 Data Agent Tools

| Ferramenta | Fonte Primária | Fallback | Descrição |
|-----------|---------------|---------|-----------| 
| `buscar_cotacao_acao(ticker)` | **Bolsai API** | yfinance | Cotação em tempo real (preço, variação, volume) |
| `buscar_indicadores_fundamentalistas(ticker)` | **Bolsai API** | yfinance | P/L, P/VP, DY, ROE, Margem Líquida |
| `buscar_top_fiis_dividend_yield(limite)` | **Bolsai API** | yfinance | Ranking de FIIs por dividend yield |
| `buscar_historico_precos(ticker, periodo)` | yfinance | — | Histórico OHLCV com retorno do período |

---

## 🔄 Fluxo de uma Consulta Completa

```
1. Usuário inicia conversa
        │
        ▼
2. Lead Advisor coleta perfil:
   nome, valor, objetivo, prazo, tolerância a risco, liquidez
        │
        ▼
3. Lead Advisor delega ao Market Analyst:
   → buscar_taxa_selic()  ──→ BCB API
   → buscar_ipca()        ──→ BCB API
   → classificar_perfil_investidor(...)
   → explicar_produto_financeiro(...)
        │
        ▼
4. Se perfil Moderado ou Arrojado:
   Lead Advisor delega ao B3 Data Agent:
   → buscar_cotacao_acao("PETR4")          ──→ Bolsai → yfinance
   → buscar_indicadores_fundamentalistas()  ──→ Bolsai → yfinance
   → buscar_top_fiis_dividend_yield()       ──→ Bolsai → yfinance
        │
        ▼
5. Lead Advisor consolida tudo e gera:
   RELATÓRIO DE RECOMENDAÇÃO PERSONALIZADO
   (perfil + macro + produtos + alocação + disclaimer)
```

---

## 🔑 Decisões de Prompt Engineering

### Lead Advisor
O prompt define um fluxo obrigatório em 3 etapas com linguagem imperativa para garantir a delegação correta:
1. **Coleta de perfil** (nome, valor, objetivo, prazo, risco, liquidez)
2. **Delegação imediata aos subagentes** — com instrução explícita de que é **PROIBIDO** responder antes de acionar os agentes e obter dados reais
3. **Geração do relatório** em formato padronizado com disclaimer obrigatório

A escolha por linguagem imperativa (`PROIBIDO`, `OBRIGATÓRIO`, `JAMAIS`) foi intencional: modelos menores tendem a "cortocircuitar" o fluxo e responder diretamente sem delegar. Instruções afirmativas e negativas explícitas forçam o comportamento correto de orquestração.

### Market Analyst
Instrução focada em:
- Uso **obrigatório** das ferramentas antes de informar qualquer taxa
- Tom educativo e didático para explicar produtos financeiros
- Proibição explícita de recomendar ativos específicos (responsabilidade do Lead Advisor)

### B3 Data Agent
Instrução focada em:
- **Confiabilidade acima de tudo** — nunca inventar cotações
- Sempre informar fonte e horário dos dados
- Avisar sobre delay de ~15 minutos quando usar yfinance (fallback)

---

## 📁 Estrutura do Projeto

```
quantum_finance/                        ← rodar "adk web" AQUI
│
├── .env                                # Variáveis de ambiente (API keys)
├── main.py                             # Ponto de entrada (chat terminal)
├── requirements.txt
├── README.md
│
└── quantum_finance/                    ← pacote Python reconhecido pelo ADK
    │
    ├── __init__.py
    ├── agent.py                        # Expõe root_agent (obrigatório ADK)
    │
    ├── agents/
    │   ├── __init__.py
    │   ├── lead_advisor.py             # 🧠 Agente Orquestrador (root_agent)
    │   ├── market_analyst.py           # 📰 Agente Pesquisador
    │   └── b3_agent.py                 # 📈 Agente de Dados B3
    │
    └── tools/
        ├── __init__.py
        ├── market_tools.py             # Ferramentas: BCB API + catálogo de produtos
        └── b3_tools.py                 # Ferramentas: Bolsai API + yfinance fallback
```

> ⚠️ **Importante:** A estrutura de dois níveis (`quantum_finance/quantum_finance/`) é exigida pelo ADK.
> O comando `adk web` deve ser executado na pasta **externa** (`quantum_finance/`), e o ADK detecta
> automaticamente o pacote interno `quantum_finance/` pelo arquivo `agent.py` que expõe `root_agent`.

---

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.11+
- Conta Google AI Studio (Gemini API Key) — projeto com billing ativado recomendado
- Conta Bolsai.com.br (gratuita — 200 req/dia)

### 1. Extraia o projeto e entre na pasta raiz

```bash
cd quantum_finance
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Edite o arquivo `.env` com suas chaves:

```env
GOOGLE_GENAI_API_KEY=sua_chave_gemini
BOLSAI_API_KEY=sua_chave_bolsai
```

### 4. Execute

**Interface Web — recomendado para demo:**
```bash
adk web
# Acesse http://localhost:8000
# Selecione o agente: quantum_finance
```

**Terminal interativo:**
```bash
python main.py
```

---

## 🌐 APIs e Integrações

| API | Tipo | Autenticação | Limite |
|-----|------|-------------|--------|
| BCB SGS (Banco Central) | REST pública | Sem chave | Sem limite |
| Bolsai (B3 oficial) | REST | API Key | 200 req/dia (free) |
| yfinance | Biblioteca Python | Sem chave | Fair use (delay 15min) |
| Google Gemini 2.5 Flash | LLM | API Key | Conforme plano |

---

## ⚠️ Disclaimer

> Este sistema é desenvolvido para fins **acadêmicos** no contexto do MBA FIAP.
> As recomendações geradas pelo sistema são **educativas** e **não constituem** aconselhamento financeiro formal.
> Sempre consulte um assessor de investimentos certificado (CEA/CFP) antes de tomar decisões de investimento.

---

## 👥 Grupo

| Nome | RM |
|------|-----|
| Ana Claudia Moser | RM 363393 |
| Giulliana de Oliveira Bevilacqua | RM 363895 |
| Laura Maria Martins Takahasi | RM 365605 |

---

## 📚 Referências

- [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- [ADK Financial Advisor Example](https://github.com/google/adk-samples/tree/main/python/agents/financial-advisor)
- [Bolsai — B3 API](https://bolsai.com.br)
- [API Banco Central do Brasil](https://dadosabertos.bcb.gov.br)
- [Google Cloud Skills Boost 32604](https://cloudskillsboost.google/focuses/32604)
