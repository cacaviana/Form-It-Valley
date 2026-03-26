# FlowQuote - Gerador Visual de Formularios e Orcamentos com IA

Sistema de criacao de formularios visuais (drag-and-drop) que gera orcamentos automaticos usando Inteligencia Artificial. Construido para a **Total Electrique** (instalacao de bornes de recharge EV no Quebec, Canada).

## O que o sistema faz

1. **Admin cria um formulario visual** (flow) com perguntas encadeadas usando drag-and-drop (SvelteFlow)
2. **Admin cadastra um CSV de precos** dos produtos/servicos — a IA usa SOMENTE esses precos (sem alucinacao)
3. **Cliente final acessa o link** do formulario, responde as perguntas e recebe um **orcamento profissional** gerado pela IA em tempo real
4. **O orcamento** mostra items, quantidades, precos, TPS/TVQ, total, recomendacoes tecnicas e notas
5. **Tudo salvo no MongoDB** com dados estruturados (items, precos, taxes) para consulta futura

## Arquitetura

```
┌──────────────────────────────────────────────────────┐
│                   FRONTEND (SvelteKit)                │
│                   localhost:5173                      │
│                                                      │
│  /admin/flows/[id]/edit  →  Editor visual de flows   │
│  /q/[slug]               →  Formulario do cliente    │
│  /api/flows/*            →  CRUD flows (MongoDB)     │
│  /api/generate-quote     →  Proxy → Backend Python   │
└────────────────────────┬─────────────────────────────┘
                         │ HTTP POST
┌────────────────────────▼─────────────────────────────┐
│                   BACKEND (Python/FastAPI)            │
│                   localhost:8001                      │
│                                                      │
│  POST /api/submissions  →  Gera orcamento com IA     │
│  GET  /api/submissions  →  Lista submissions         │
│                                                      │
│  PydanticAI Agent  →  Output estruturado (QuoteOutput)│
│  CSV pricing       →  Precos reais, sem alucinacao   │
│  Output validator  →  Recalcula totais e taxes       │
└──────────────────────────────────────────────────────┘
                         │
                    MongoDB Atlas
                    (flows, submissions)
```

## Stack Tecnica

| Camada | Tecnologia |
|--------|-----------|
| Frontend | SvelteKit + Svelte 5 (runes) + Tailwind CSS |
| Flow Builder | @xyflow/svelte (SvelteFlow) |
| Backend | Python 3.12 + FastAPI + Motor (async MongoDB) |
| Agente IA | PydanticAI com output parsing estruturado |
| Banco | MongoDB Atlas |
| Testes E2E | Playwright |

## Pre-requisitos

- **Node.js** 18+ (recomendado 22)
- **Python** 3.11+ (recomendado 3.12)
- **MongoDB Atlas** (conta com cluster — pode ser free tier)
- **API Key** de IA: OpenAI (GPT-4o-mini) ou Anthropic (Claude)

## Setup Rapido

### 1. Clonar o repositorio

```bash
git clone <repo-url>
cd frontendSvelteFlow
```

### 2. Backend (Python)

```bash
cd backend

# Criar e ativar virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variaveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais (MongoDB URI, API keys)

# Rodar o backend
uvicorn main:app --host 0.0.0.0 --port 8001
```

O backend roda em `http://localhost:8001`.

### 3. Frontend (SvelteKit)

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variaveis de ambiente
cp .env.example .env
# Editar .env com sua MongoDB URI e URL do backend

# Rodar em modo desenvolvimento
npm run dev
```

O frontend roda em `http://localhost:5173`.

### 4. Acessar o sistema

- **Editor de flows (admin):** `http://localhost:5173/admin`
- **Formulario do cliente:** `http://localhost:5173/q/<slug-do-flow>`

## Variaveis de Ambiente

### Backend (`backend/.env`)

| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| `MONGODB_URI` | Connection string do MongoDB Atlas | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGODB_DATABASE` | Nome do banco | `flowquote` |
| `OPENAI_API_KEY` | Chave da API OpenAI | `sk-proj-...` |
| `OPENAI_MODEL` | Modelo OpenAI | `gpt-4o-mini` |
| `AI_PROVIDER` | Provedor de IA (`openai` ou `anthropic`) | `openai` |
| `ANTHROPIC_API_KEY` | Chave Anthropic (se usar Claude) | `sk-ant-...` |
| `ANTHROPIC_MODEL` | Modelo Anthropic | `claude-sonnet-4-20250514` |
| `CORS_ORIGINS` | Origens CORS permitidas | `["http://localhost:5173"]` |

### Frontend (`frontend/.env`)

| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| `MONGODB_URI` | Connection string do MongoDB Atlas | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGODB_DATABASE` | Nome do banco | `flowquote` |
| `BACKEND_URL` | URL do backend Python | `http://localhost:8001` |

**Importante:** Frontend e Backend compartilham o MESMO MongoDB Atlas.

## Estrutura de Pastas

```
frontendSvelteFlow/
├── backend/                     # API Python/FastAPI
│   ├── main.py                  # Entry point + CORS + lifespan
│   ├── requirements.txt         # Dependencias Python
│   ├── config/
│   │   ├── settings.py          # Pydantic Settings (.env)
│   │   └── database.py          # Motor MongoDB client
│   ├── routers/
│   │   ├── flow.py              # CRUD flows
│   │   └── submission.py        # Submissions + quote generation
│   ├── services/
│   │   ├── submission_service.py # Orquestracao
│   │   └── quote_generator.py   # Agente PydanticAI
│   ├── dtos/
│   │   └── submission/
│   │       └── create_submission/
│   │           ├── request.py   # Pydantic request model
│   │           └── response.py  # Pydantic response model (output parsing)
│   ├── factories/               # Criacao de documentos
│   ├── mappers/                 # MongoDB <-> Response
│   └── data/repositories/       # CRUD MongoDB
│
├── frontend/                    # SvelteKit App
│   ├── src/
│   │   ├── lib/
│   │   │   ├── dto/flows/       # Types + Request DTOs
│   │   │   ├── stores/          # flowBuilder store (Svelte 5 runes)
│   │   │   ├── services/        # FlowsService, SubmissionsService
│   │   │   └── data/repositories/ # API calls
│   │   └── routes/
│   │       ├── admin/flows/[id]/edit/ # Editor visual de flows
│   │       ├── q/[slug]/        # Formulario publico do cliente
│   │       └── api/
│   │           ├── flows/       # CRUD flows (SvelteKit → MongoDB)
│   │           ├── generate-quote/ # Proxy → Backend Python
│   │           └── submissions/ # CRUD submissions
│   ├── tests/
│   │   └── quote-e2e.spec.ts    # Testes E2E Playwright
│   └── playwright.config.ts
│
└── README.md                    # Este arquivo
```

## Fluxo Completo (Ponta a Ponta)

### 1. Admin cria o formulario

1. Acessa `/admin` → lista de flows
2. Cria ou edita um flow no editor visual (drag-and-drop)
3. Adiciona nodes: Start → Questions → End (tipo "quote" ou "specialist")
4. Cada Question tem tipo (single_choice, yes_no, number) e opcoes
5. Clica no botao **"Catalogue de prix (CSV)"** para fazer upload do CSV de precos
6. O CSV tem formato: `produto,preco,unidade,categoria`
7. Salva o flow

### 2. Cliente responde o formulario

1. Acessa `/q/<slug>` (link compartilhavel)
2. Preenche dados pessoais (nome, email, telefone, endereco)
3. Clica "Commencer" e responde as perguntas
4. As respostas determinam o caminho no flow (branching)

### 3. IA gera o orcamento

1. Ao chegar no End Node tipo "quote", o frontend chama `/api/generate-quote`
2. O proxy SvelteKit encaminha para o backend Python (`POST /api/submissions`)
3. O backend:
   - Busca o flow no MongoDB (pega o CSV de precos e businessContext do EndNode)
   - Cria uma submission via Factory
   - Chama o **PydanticAI Agent** com:
     - CSV de precos como catalogo (source of truth)
     - Respostas do cliente
     - Regras de negocio do EndNode
   - O agente retorna `QuoteOutput` (output parsing Pydantic)
   - O **output validator** recalcula todos os subtotais e taxes (TPS 5%, TVQ 9.975%)
   - Salva submission + quote no MongoDB
4. O frontend exibe o orcamento num **card profissional** com:
   - Tabela de items (produto, quantidade, preco)
   - Sous-total, TPS, TVQ, **Total**
   - Recomendacoes tecnicas da IA
   - Notas e condicoes
   - Botao "Imprimer / PDF"

## CSV de Precos (Formato)

O admin faz upload de um CSV com os precos dos produtos. A IA usa SOMENTE esses precos.

```csv
produto,preco,unidade,categoria
Borne 16A Level 1,499,unidade,borne
Borne 32A Level 2,699,unidade,borne
Borne 48A Level 2,899,unidade,borne
Controller DCC-9,699,unidade,accessoire
Installation murale exterieure,490,unidade,installation
Installation sur poteau,690,unidade,installation
Cablage par pied,9,pied,cablage
Deplacement,69,unidade,deplacement
```

Um template CSV pode ser baixado direto no editor de flows.

## Testes E2E (Playwright)

```bash
cd frontend

# Instalar browsers Playwright (primeira vez)
npx playwright install chromium

# Rodar os testes (backend + frontend devem estar rodando)
npx playwright test tests/quote-e2e.spec.ts
```

### Testes incluidos:
1. **Step 1:** Upload CSV via API e verifica persistencia
2. **Step 2:** Modal de CSV abre no editor visual
3. **Step 3:** Cliente preenche formulario → IA gera orcamento com precos do CSV
4. **Step 4:** Verifica submission salva no backend com status "quoted"

## Agente de IA (PydanticAI)

O agente usa **PydanticAI** com output parsing estruturado:

- **Input:** CSV de precos + respostas do cliente + regras de negocio
- **Output:** `QuoteOutput` (Pydantic model com items, subtotal, taxes, total, recommandations)
- **Validacao:** O `output_validator` recalcula matematicamente todos os valores
- **Fallback:** Se a IA falhar, gera um devis basico sem precos e marca para contato manual

Provedores suportados: **OpenAI** (GPT-4o-mini) e **Anthropic** (Claude Sonnet).

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| Backend nao inicia | Verificar `.env` (MongoDB URI, API keys) |
| Quote nao gera | Verificar se OPENAI_API_KEY ou ANTHROPIC_API_KEY esta no `.env` do backend |
| Frontend nao conecta no backend | Verificar `BACKEND_URL=http://localhost:8001` no `.env` do frontend |
| Erro 422 ao gerar quote | Verificar que todos os `answers[].value` sao strings (nao numeros) |
| `__pycache__` impede reload | Deletar `backend/**/__pycache__/` e reiniciar uvicorn |
