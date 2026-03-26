# Total Électrique — Documentação de Fluxo

## O que o sistema faz

Sistema web para **gerar orçamentos automatizados de instalação de estações de carregamento elétrico (bornes)** no Quebec, Canadá, usando IA. O cliente responde um questionário e recebe um orçamento personalizado — ou é encaminhado a um especialista humano.

---

## Fluxo Principal

### 1. Landing Page (`/`)
Cliente preenche: **nome, email, telefone, endereço** → clica em **"Commencer l'évaluation"** → dados salvos no `sessionStorage` → redireciona para `/chat`.

---

### 2. Questionário (`/chat`) — 8 perguntas sequenciais

| # | Pergunta | Tipo |
|---|----------|------|
| P1 | Região (Lanaudière / Est Montréal / Laval / **Autre**) | Single choice |
| P2 | Marca do painel elétrico | Single choice |
| P3 | Amperagem do painel (60A / 100A / 150A / 200A / 320A / 400A) | Single choice |
| P4 | Espaços livres no painel? (Sim / Duplo / **Não**) | Single choice |
| P5 | Tem spa? | Sim/Não |
| P6 | Já tem borne instalada? | Sim/Não |
| P6a | Se sim: tipo da borne (Plug-in / Hardwired) | Single choice |
| P6b | Se sim: amperagem da borne | Single choice |
| P7 | Local da instalação (Parede / Poste / **Interior**) | Single choice |
| P8 | Distância da entrada elétrica (em pés) | Número |

---

## Bifurcações (onde o fluxo muda)

```
P1: Região = "Autre"
  → ESPECIALISTA  (região não atendida)

P4: Espaços livres = "Não"
  → ESPECIALISTA  (painel cheio, precisa avaliação)

P6: Tem borne = "Não"
  → Pula P6a e P6b, vai direto para P7

P7: Local = "Interior"
  → ESPECIALISTA  (instalação interna é mais complexa)

Qualquer outra combinação
  → Gera orçamento com IA
```

---

## Destino Final A — Especialista Necessário

Mostra mensagem explicativa + dados do cliente confirmados → envia `POST /api/support/leads/analyze` salvando o lead para o admin entrar em contato.

---

## Destino Final B — Orçamento Gerado

1. Chama `POST /api/chat/analyze-quote` (IA do backend)
2. Se falhar → fallback com **cálculo local**
3. Exibe orçamento formatado + botão **Download .txt**

**Cálculo de preço:**
```
Total = borne + controller de carga (se necessário) + instalação + (distância × $9/pé) + deslocamento
```

**Recomendação de borne** é baseada na amperagem do painel + se tem spa:

| Painel | Spa | Recomendação | Controller |
|--------|-----|--------------|------------|
| 60A | Qualquer | Borne 16A | Obrigatório |
| 100A | Não | 16A direto ou 32A + Controller | Opcional |
| 100A | Sim | 16A + Controller ou Upgrade | Sim |
| 150A | Não | até 40A direto | Não |
| 150A | Sim | Controller obrigatório ou Upgrade 200A | Sim |
| 200A | Não | até 60A direto | Não |
| 200A | Sim | 32A direto ou 48A+ com Controller | Opcional |
| 320A | Qualquer | até 60A direto | Não |
| 400A | Qualquer | até 100A direto | Não |

---

## Área Admin (`/admin` → `/painel`)

Login com usuário/senha → token JWT no `sessionStorage` → acesso ao painel com 5 abas:

| Aba | Função |
|-----|--------|
| Documentos | Upload e gerenciamento de PDFs para o RAG |
| Devis | Ver todos os orçamentos gerados, mudar status |
| Leads | Ver clientes encaminhados a especialista, mudar status |
| Emails | Configurar emails de notificação |
| Preços | Atualizar tabela de preços |

---

## Diagrama resumido

```
/  ──────[dados cliente]──────► /chat
                                   │
                          P1/P4/P7 │ condicional
                    ┌──────────────┴──────────────┐
                    ↓                             ↓
             ESPECIALISTA                  ORÇAMENTO COM IA
         (POST support/leads)           (POST chat/analyze-quote)
         Mensagem + contato            Download .txt do orçamento

/admin ──[login JWT]──► /painel
                         ├─ Documentos (RAG PDFs)
                         ├─ Devis (orçamentos)
                         ├─ Leads (especialistas)
                         ├─ Emails
                         └─ Preços
```

---

## Onde cada lógica vive

### Frontend (SvelteKit)
- **Toda a lógica do questionário** — perguntas, ordem, bifurcações, pulo de perguntas
- **Cálculo de recomendação de borne** — baseado em amperagem + spa
- **Cálculo de preço** — tabela de preços local (`QuestionnaireLogic`)
- **Fallback de orçamento** — gera o orçamento localmente se a IA falhar
- **Validações de formulário** — campos obrigatórios, distância numérica
- **Gerenciamento de estado** — via `sessionStorage` e variáveis locais

### Backend (FastAPI + IA)
- **Geração do orçamento com IA** — `POST /api/chat/analyze-quote` (RAG + LLM)
- **Armazenamento de leads** — `POST /api/support/leads/analyze`
- **Autenticação JWT** — `POST /api/auth/login`
- **Gestão de documentos RAG** — upload, indexação no Pinecone
- **Persistência** — MongoDB para quotes, leads, usuários

### Ponto-chave
> O frontend **não depende do backend para funcionar**: toda a lógica de negócio (perguntas, cálculo, preço) está implementada localmente. O backend é chamado para **enriquecer o orçamento com IA** e **persistir os dados**. Se o backend estiver offline, o sistema ainda gera orçamentos via fallback local.

---

## Storage utilizado

| Chave | Onde | Conteúdo |
|-------|------|----------|
| `clientData` | sessionStorage | Dados do cliente (nome, email, telefone, endereço) |
| `adminToken` | sessionStorage | Token JWT do admin |
| `adminUser` | sessionStorage | Nome do usuário admin logado |
| `theme` | localStorage | Tema da interface (light/dark) |
