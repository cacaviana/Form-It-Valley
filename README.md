# Form IT Valley - Formulario de Qualificacao e Agendamento

Sistema de formularios visuais com agendamento inteligente para a **IT Valley — Escola de Tecnologia**. O lead responde perguntas de qualificacao e, ao final, escolhe data e horario para uma reuniao via calendario integrado com Google Calendar.

## O que o sistema faz

1. **Admin cria um formulario visual** (flow) com perguntas de qualificacao usando drag-and-drop (SvelteFlow)
2. **Lead acessa o link** do formulario, responde as perguntas de qualificacao
3. **Ao final, abre um calendario** onde o lead escolhe a data e horario disponivel
4. **Reuniao criada automaticamente** no Google Calendar com os dados do lead
5. **Tudo salvo no MongoDB** — dados do lead, respostas e agendamento

## Arquitetura

```
┌──────────────────────────────────────────────────────┐
│                   FRONTEND (SvelteKit)                │
│                   localhost:5173                      │
│                                                      │
│  /admin/scheduling         →  Dashboard de agendamento│
│  /admin/flows/[id]/edit    →  Editor visual de flows  │
│  /q/[slug]                 →  Formulario do lead      │
│  /api/flows/*              →  CRUD flows (MongoDB)    │
│  /api/scheduling           →  Datas/slots + booking   │
└────────────────────────────┬─────────────────────────┘
                             │ HTTP
┌────────────────────────────▼─────────────────────────┐
│                   BACKEND (Python/FastAPI)            │
│                   localhost:8001                      │
│                                                      │
│  CRUD flows e submissions                            │
│  Integracao Google Calendar (slots disponiveis)      │
└──────────────────────────────────────────────────────┘
                             │
                        MongoDB Atlas
                        (flows, submissions, schedulings)
```

## Stack Tecnica

| Camada | Tecnologia |
|--------|-----------|
| Frontend | SvelteKit + Svelte 5 (runes) + Tailwind CSS |
| Flow Builder | @xyflow/svelte (SvelteFlow) |
| Backend | Python 3.12 + FastAPI + Motor (async MongoDB) |
| Calendario | Google Calendar API (service account) |
| Banco | MongoDB Atlas |

## Pre-requisitos

- **Node.js** 18+ (recomendado 22)
- **Python** 3.11+ (recomendado 3.12)
- **MongoDB Atlas** (conta com cluster — pode ser free tier)
- **Google Calendar** service account (para integracao de agenda)

## Setup Rapido

### 1. Clonar o repositorio

```bash
git clone https://github.com/cacaviana/Form-It-Valley.git
cd Form-It-Valley
```

### 2. Backend (Python)

```bash
cd backend

# Criar e ativar virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variaveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais (MongoDB URI, etc.)

# Rodar o backend
python main.py
```

O backend roda em `http://localhost:8001`.

### 3. Frontend (SvelteKit)

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variaveis de ambiente
cp .env.example .env
# Editar .env com sua MongoDB URI

# Rodar em modo desenvolvimento
npm run dev
```

O frontend roda em `http://localhost:5173`.

### 4. Acessar o sistema

- **Dashboard de agendamento:** `http://localhost:5173/admin/scheduling`
- **Formulario do lead:** `http://localhost:5173/q/<slug-do-flow>`

## Fluxo Completo

### 1. Admin cria o formulario

1. Acessa `/admin/scheduling` → lista de flows de agendamento
2. Cria ou edita um flow no editor visual (drag-and-drop)
3. Adiciona nodes: Start → Questions → End (tipo "scheduling")
4. Cada Question tem tipo (single_choice, yes_no, number) e opcoes
5. Salva o flow e publica

### 2. Lead responde o formulario

1. Acessa `/q/<slug>` (link compartilhavel)
2. Preenche dados pessoais (nome, email, telefone)
3. Responde as perguntas de qualificacao
4. Ao final, escolhe data e horario no calendario
5. Reuniao confirmada automaticamente

### 3. Admin acompanha

1. Acessa `/admin/scheduling` → aba "Reservations"
2. Ve todos os agendamentos com status (confirmado, cancelado, concluido)
3. Dados do lead e respostas de qualificacao salvos

## Variaveis de Ambiente

### Backend (`backend/.env`)

| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| `MONGODB_URI` | Connection string do MongoDB Atlas | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGODB_DATABASE` | Nome do banco | `flowquote` |
| `CORS_ORIGINS` | Origens CORS permitidas | `["http://localhost:5173"]` |

### Frontend (`frontend/.env`)

| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| `MONGODB_URI` | Connection string do MongoDB Atlas | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGODB_DATABASE` | Nome do banco | `flowquote` |
