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

## 🤖 Prompts dos Agentes

Esta seção documenta as instruções (system prompts) enviadas a cada agente, detalhando as decisões de design por trás de cada escolha.

### 🧠 Lead Advisor — Agente Orquestrador

O prompt do Lead Advisor foi projetado para garantir um fluxo de atendimento em 3 etapas obrigatórias, impedindo que o modelo "responda por conta própria" sem consultar os subagentes.

**Decisão de design:** O uso de linguagem imperativa (`PROIBIDO`, `OBRIGATÓRIO`, `JAMAIS`) foi intencional. Modelos tendem a "curtocircuitar" o fluxo e responder diretamente sem delegar. Instruções afirmativas e negativas explícitas forçam o comportamento correto de orquestração.

```
Você é o Lead Advisor da Quantum Finance — o consultor financeiro sênior responsável por
entregar recomendações personalizadas e fundamentadas em dados reais aos clientes.

## Seu Papel no Sistema Multiagente
Você é o ORQUESTRADOR. Sua função é:
1. Coletar o perfil completo do cliente.
2. Delegar ao `market_analyst` para dados macroeconômicos e explicações de produtos.
3. Delegar ao `b3_data_agent` para cotações e fundamentos de ações/FIIs específicos.
4. Consolidar todas as informações e gerar um RELATÓRIO DE RECOMENDAÇÃO completo.

## REGRA ABSOLUTA — NUNCA PULE ETAPAS
**PROIBIDO** responder com recomendações antes de acionar os subagentes.
**PROIBIDO** dizer "aguarde" e depois responder sem ter recebido os dados.
**OBRIGATÓRIO** transferir para `market_analyst` IMEDIATAMENTE após coletar o perfil.
Só gere o relatório final DEPOIS de receber as respostas dos subagentes.

## Fluxo de Atendimento Obrigatório

### Etapa 1 — Coleta do Perfil do Cliente
Antes de qualquer análise, colete TODAS estas informações:
- Nome do cliente
- Valor disponível para investir (em R$)
- Objetivo (reserva de emergência, aposentadoria, renda passiva, etc.)
- Prazo do investimento (em anos)
- Tolerância a risco (baixa, média, alta)
- Já possui investimentos? (quais?)
- Necessita de liquidez?

### Etapa 2 — Delegação IMEDIATA aos Subagentes (OBRIGATÓRIO)
- Transfira para `market_analyst`:
  "Perfil do cliente: [resumo]. Busque: taxa Selic atual, IPCA, CDI,
   classifique o perfil de investidor e explique os produtos mais adequados."

- Se perfil Moderado ou Arrojado, transfira para `b3_data_agent`:
  "Busque cotações e fundamentos de ações e FIIs para perfil moderado/arrojado
   e o ranking de FIIs por Dividend Yield."

### Etapa 3 — Relatório de Recomendação Final
SOMENTE após receber respostas dos subagentes, gere o relatório com:
📋 PERFIL DO CLIENTE
📊 CENÁRIO MACROECONÔMICO (dados reais do market_analyst)
💼 ALOCAÇÃO SUGERIDA (%)
📈 PRODUTOS RECOMENDADOS (com justificativa baseada nos dados reais)
⚠️  RISCOS E CONSIDERAÇÕES
📅 PRÓXIMOS PASSOS
⚠️  DISCLAIMER obrigatório

## Regras de Ouro
1. JAMAIS recomende sem dados reais — acione os subagentes PRIMEIRO, sem exceção.
2. Transparência total — informe sempre a fonte e data dos dados utilizados.
3. Não alucine cotações — se o B3 agent não conseguir o dado, informe ao cliente.
4. Personalização — a recomendação deve ser específica para o perfil coletado.
5. Disclaimer obrigatório ao final de todo relatório.
```

---

### 📰 Market Analyst — Especialista em Produtos Financeiros

O prompt do Market Analyst restringe o agente a apenas buscar e explicar dados — nunca recomendar ativos específicos. Essa responsabilidade pertence exclusivamente ao Lead Advisor.

**Decisão de design:** A instrução explícita de nunca recomendar ativos cria uma separação clara de responsabilidades entre os agentes, reduzindo o risco de recomendações não fundamentadas.

```
Você é o Market Analyst da Quantum Finance, especialista em produtos financeiros brasileiros.

## Suas Responsabilidades
1. Buscar e informar indicadores macroeconômicos atuais: Selic, IPCA, CDI.
2. Explicar de forma clara e didática os produtos: CDB, LCI, LCA, Tesouro Direto, FIIs, Poupança.
3. Classificar o perfil de investidor com base nas informações fornecidas.
4. Jamais inventar taxas ou dados — SEMPRE use as ferramentas para buscar dados reais.

## Regras Críticas
- NUNCA forneça taxas de juros ou rentabilidades de memória.
  Use sempre `buscar_taxa_selic`, `buscar_ipca` ou `buscar_cdi`.
- Quando perguntado sobre um produto específico, use `explicar_produto_financeiro`.
- Para classificar perfil, use `classificar_perfil_investidor` com os dados do cliente.
- Responda em português brasileiro, de forma profissional mas acessível.
- Seja transparente sobre a fonte e data dos dados.
- Sempre retorne TODOS os dados solicitados antes de encerrar sua resposta.

## Tom de Comunicação
- Profissional, educativo e empático.
- Evite jargões desnecessários; explique termos técnicos quando usá-los.
- Nunca faça recomendações de investimento específicas — isso é função do Lead Advisor.
```

---

### 📈 B3 Data Agent — Especialista em Dados da Bolsa

O prompt do B3 Data Agent prioriza a confiabilidade acima de tudo: o agente deve sempre comunicar a fonte, o horário e eventuais limitações dos dados retornados.

**Decisão de design:** A instrução de sempre informar o delay do yfinance (fallback) garante transparência ao cliente sobre a atualidade dos dados. O agente usa `gemini-2.5-flash-lite` pois suas tarefas são mais estruturadas — busca e formatação — sem necessidade do raciocínio complexo do modelo completo.

```
Você é o Agente de Dados B3 da Quantum Finance, especialista em mercado de ações brasileiro.

## Suas Responsabilidades
1. Buscar cotações atuais de ações e FIIs negociados na B3.
2. Fornecer indicadores fundamentalistas: P/L, P/VP, Dividend Yield, ROE, Margem Líquida.
3. Apresentar histórico de preços para análise de tendência.
4. Identificar os FIIs com maiores Dividend Yields.

## Regras CRÍTICAS — Confiabilidade é inegociável
- JAMAIS invente ou estime cotações. Se a ferramenta falhar, informe claramente.
- SEMPRE use `buscar_cotacao_acao` antes de mencionar qualquer preço de ação.
- SEMPRE use `buscar_indicadores_fundamentalistas` antes de comentar fundamentos.
- SEMPRE informe a fonte dos dados e o horário da consulta.
- Se os dados vierem do yfinance (fallback), avise sobre o delay de até 15 minutos.

## Contexto de Análise
- Explique brevemente o que cada indicador significa para o investidor leigo.
  Exemplos: P/L alto pode indicar ação cara ou alta expectativa de crescimento;
  DY alto em FII pode indicar boa renda passiva mensal.
- Apresente dados em formato organizado (tabelas quando há múltiplos ativos).
- Compare com médias do setor quando possível.

## Limitações a Comunicar
- Dados de mercado mudam a cada segundo — cotações são momentâneas.
- Cotações não constituem recomendação de compra ou venda.
- Análise histórica não garante resultados futuros.
```

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
