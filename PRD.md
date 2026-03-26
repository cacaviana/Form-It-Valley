# PRD — FlowQuote: Construtor Visual de Orçamentos com IA

> **Versão:** 2.0
> **Data:** 2026-03-11
> **Autor:** IT Valley
> **Status:** Em desenvolvimento (frontend funcional)

---

## 1. Visão do Produto

**FlowQuote** é uma plataforma SaaS que permite a qualquer empresa criar formulários inteligentes de orçamento de forma visual, usando arrastar e soltar, com bifurcações condicionais e geração automática de orçamentos por IA.

**Em uma frase:** *O admin desenha o fluxo, o cliente responde, a IA gera o orçamento.*

---

## 2. Problema

Empresas de serviço (eletricistas, encanadores, construtoras, instaladores) precisam de orçamentos rápidos e padronizados. Hoje elas:

- Fazem orçamentos manualmente por telefone ou WhatsApp
- Perdem leads por demora na resposta
- Não conseguem escalar o atendimento
- Cada orçamento exige conhecimento técnico do atendente

**FlowQuote resolve** colocando o cliente para responder um questionário visual e deixando a IA fazer o trabalho técnico.

---

## 3. Público-Alvo

### 3.1 Admin (Dono do negócio)
- Cria e edita o fluxo de perguntas visualmente
- Define bifurcações: "se resposta X, vá para pergunta Y"
- Configura o contexto de negócio para a IA
- Gerencia orçamentos gerados e leads de suporte
- Atualiza preços e regras sem mexer em código

### 3.2 Cliente Final (Consumidor)
- Acessa um link público
- Responde o questionário passo a passo
- Recebe o orçamento em segundos
- Faz download do orçamento em PDF/TXT

---

## 4. Funcionalidades

### 4.1 Builder Visual (Admin) — SvelteFlow

O coração do sistema. O admin constrói o fluxo de perguntas arrastando nós em um canvas visual.

#### Tipos de Nó

| Nó | Cor | Função | Status |
|----|-----|--------|--------|
| **Início** | Verde (`green-500`) | Ponto de entrada do fluxo. Único por fluxo. Coleta nome, email e telefone do cliente. | Implementado |
| **Pergunta** | Azul (`blue-500`) | Uma pergunta ao cliente. 9 tipos suportados (ver abaixo). Handles individuais por opção para roteamento condicional. | Implementado |
| **Mensagem** | Cinza (`gray-500`) | Exibe um texto informativo ao cliente sem esperar resposta. Pode ser marcado como "Especialista" (cor vermelha) para desvio com contato humano. | Implementado |
| **Fim** | Roxo (`purple-500`) | Nó terminal. 3 subtipos: geração de orçamento por IA, contato com especialista, ou agradecimento. | Implementado |

> **Nota:** Os nós "Condição" e "Especialista" do PRD v1 foram absorvidos pela implementação atual. A bifurcação condicional é feita diretamente pelas **arestas de saída do nó Pergunta** (cada opção gera um handle de saída). O desvio para especialista é feito via nó **Mensagem** com flag `isSpecialist: true` ou nó **Fim** com `endType: 'specialist'`.

#### 9 Tipos de Pergunta Implementados

| Tipo | Código | Descrição |
|------|--------|-----------|
| Escolha Única | `single_choice` | Botões de seleção — cada opção pode rotear para um caminho diferente |
| Sim / Não | `yes_no` | Duas opções fixas |
| Número | `number` | Input numérico |
| Texto Livre | `text` | Input de texto |
| Múltipla Escolha | `multiple_choice` | Checkboxes — cada opção pode rotear |
| Data | `date` | Seletor de data |
| Avaliação | `rating` | Escala numérica (máximo configurável) |
| Dropdown | `dropdown` | Menu suspenso — cada opção pode rotear |
| Foto | `photo` | Upload de imagem |

#### Handles de Saída Inteligentes

Para perguntas do tipo `single_choice`, `multiple_choice` e `dropdown`:
- Se **5 ou menos opções**: cada opção gera um **handle de saída individual** no nó, permitindo roteamento visual direto por opção
- Se **mais de 5 opções**: exibe resumo compacto ("X opções") com handle de saída único
- Demais tipos de pergunta: handle de saída único (bottom)

#### Arestas (Conexões)

- Cada aresta liga um nó ao próximo
- Arestas de saída de **Pergunta** usam `sourceHandle` com o ID da opção para roteamento condicional
- Exemplo: nó "Região" tem arestas de saída por opção: "Laval" → próxima pergunta, "Montréal" → próxima pergunta, "Autre" → nó Especialista

#### Configuração de cada Nó Pergunta

```
Título:        "Qual a amperagem do seu painel?"
Tipo:          single_choice | yes_no | number | text | multiple_choice | date | rating | dropdown | photo
Opções:        [{ id, label, value }, ...]  (para tipos com opções)
Obrigatória:   Sim/Não (checkbox)
Dica (tooltip): "Verifique na tampa do seu painel elétrico"
Rating máximo:  número (apenas para tipo rating)
```

#### Configuração do Nó Fim (Orçamento)

```
Tipo de fim:     generate_quote | specialist | thank_you
Contexto do negócio (businessContext):
  "Somos a Total Électrique, empresa de instalação de bornes
   de carregamento elétrico no Quebec. Nossos preços base são:
   - Borne 16A: $499
   - Borne 32A: $699
   - Instalação parede: $490
   - Cabo: $9/pé
   ..."

Instrução para IA (aiInstruction):
  "Gere um orçamento profissional em francês, detalhando cada
   item, com subtotais e total final. Inclua recomendações
   técnicas baseadas nas respostas."

Mensagem de especialista (specialistMessage):
  "Um especialista entrará em contato em até 24h."
```

#### Ações no Builder (Implementadas)

- **Adicionar nó** via toolbar (botões: Pergunta, Mensagem, Fim)
- **Conectar** nós clicando e arrastando entre handles
- **Clicar** em um nó para editar suas propriedades no **painel lateral direito** (NodeEditor)
- **Deletar** nó pelo painel de edição (exceto nó Início)
- **Zoom**, **pan** e **minimap** no canvas (via SvelteFlow controls)
- **Salvar** grava o fluxo via serviço (mock ou API REST)
- **Editar nome** do fluxo diretamente no header

#### Ações no Builder (Planejadas — não implementadas)

- Publicar / despublicar fluxo
- Preview do fluxo como cliente
- Duplicar fluxo
- Histórico de versões
- Arrastar nó do painel para o canvas (drag & drop)

---

### 4.2 Executor de Fluxo (Cliente Final)

O cliente acessa a URL pública (`/q/:slug`) e o sistema renderiza o fluxo pergunta por pergunta.

#### Tela Inicial (Implementada)
```
┌─────────────────────────────────────────┐
│  Obtenez votre devis en quelques        │
│  minutes!                               │
│                                         │
│  Nom:      [________________]          │
│  E-mail:   [________________]          │
│  Téléphone:[________________]          │
│                                         │
│  [Commencer]                            │
└─────────────────────────────────────────┘
```
> Coleta nome, email e telefone. Endereço removido da v1 (simplificação).

#### Tela de Pergunta (Implementada)
```
┌─────────────────────────────────────────┐
│  [████████████░░░░░░░] 62%              │
│                                         │
│  Pergunta atual renderizada             │
│  conforme o tipo:                       │
│                                         │
│  single_choice → botões grid 2 colunas  │
│  yes_no → botões Sim / Não             │
│  number → input numérico + Continuer   │
│  text → input texto + Continuer        │
│                                         │
│  [← Retour]                            │
└─────────────────────────────────────────┘
```

#### Tipos renderizados no executor

| Tipo | Renderização |
|------|-------------|
| `single_choice` | Grid de botões (2 colunas) — clique avança automaticamente |
| `yes_no` | Dois botões: Oui / Non |
| `number` | Input numérico + botão "Continuer" |
| `text` | Input texto + botão "Continuer" |
| `multiple_choice` | *Não implementado no executor* |
| `date` | *Não implementado no executor* |
| `rating` | *Não implementado no executor* |
| `dropdown` | *Não implementado no executor* |
| `photo` | *Não implementado no executor* |

#### Tela Especialista / Mensagem com Especialista (Implementada)
```
┌─────────────────────────────────────────┐
│  Un spécialiste vous contactera         │
│                                         │
│  [Mensagem configurada pelo admin]     │
│                                         │
│  Vos données ont été enregistrées.     │
│  Nous vous contacterons sous 24h.      │
└─────────────────────────────────────────┘
```

#### Tela Orçamento Gerado (Implementada — versão simplificada)
```
┌─────────────────────────────────────────┐
│  Votre devis est prêt!                 │
│                                         │
│  [Texto do orçamento gerado            │
│   localmente a partir do               │
│   businessContext do nó Fim]           │
│                                         │
│  Merci, [nome]! Nous vous              │
│  contacterons à [email].              │
└─────────────────────────────────────────┘
```
> **Nota:** Atualmente o executor gera o texto do orçamento localmente no frontend (concatena businessContext + aiInstruction). A integração real com LLM (OpenAI/Anthropic) depende do backend.

#### Lógica de Execução (Implementada)

```
1. Carrega o fluxo por slug (mock ou API)
2. Fase "form": coleta nome, email, telefone
3. Fase "questions": navega pelo grafo seguindo as arestas
   a. Encontra o nó Início e segue a aresta de saída
   b. Para cada nó:
      - Se PERGUNTA → renderiza e espera resposta
        - Para single_choice: segue aresta com sourceHandle = opção escolhida
        - Para outros tipos: segue aresta sem sourceHandle específico
      - Se MENSAGEM → exibe texto
        - Se isSpecialist → exibe tela de especialista e para
        - Senão → exibe mensagem e segue automaticamente
      - Se FIM → vai para fase "end"
   c. Botão "Retour" permite voltar à pergunta anterior
4. Fase "end": exibe resultado conforme endType do nó
5. Barra de progresso baseada em proporção de respostas vs total estimado de nós
```

---

### 4.3 Painel Admin (Gestão) — Planejado

> **Status:** Não implementado. Apenas a listagem de fluxos existe.

#### Tela Implementada: Lista de Fluxos (`/admin/flows`)
- Cards com nome, status (draft/published/archived), slug e contagem de nós
- Botão "Criar novo fluxo"
- Link para editar cada fluxo

#### Telas Planejadas (não implementadas)

| # | Tela | Rota | Descrição |
|---|------|------|-----------|
| A1 | Login | `/admin` | Autenticação do admin |
| A2 | Dashboard | `/admin/dashboard` | Resumo geral com métricas |
| A5 | Orçamentos | `/admin/quotes` | Tabela de orçamentos com filtros e status |
| A6 | Leads | `/admin/leads` | Tabela de leads de especialista |
| A7 | Configurações | `/admin/settings` | Dados da empresa, logo, cores, API keys |
| A8 | Preview | `/admin/flows/:id/preview` | Testar o fluxo como cliente |

#### Dashboard Principal (Planejado)

| Seção | O que mostra |
|-------|-------------|
| **Resumo** | Total de orçamentos hoje/semana/mês, taxa de conclusão, leads pendentes |
| **Orçamentos** | Lista de todos os orçamentos com status: pendente, atendido, aprovado, rejeitado |
| **Leads** | Contatos que caíram no caminho "Especialista" — aguardando ligação |
| **Fluxos** | Lista de fluxos criados com status: rascunho, publicado, arquivado |
| **Configurações** | Dados da empresa, logo, cores, emails de notificação, chaves de API |

#### Status de Orçamento (Planejado)

```
Pendente → Atendido → Aprovado
                   └→ Rejeitado
```

#### Notificações (Planejadas)

- Email ao admin quando novo orçamento é gerado
- Email ao admin quando novo lead de especialista é criado
- Email ao cliente com cópia do orçamento (opcional, configurável)

---

### 4.4 Geração de Orçamento com IA

#### Fluxo da IA (Planejado)

```
Respostas do cliente (JSON)
         +
Contexto do negócio (businessContext do nó Fim)
         +
Instrução de formatação (aiInstruction do nó Fim)
         ↓
    Prompt montado dinamicamente
         ↓
    LLM (OpenAI / Anthropic)
         ↓
    Orçamento formatado
         ↓
    Salvo no MongoDB + exibido ao cliente
```

#### Implementação Atual (Frontend Mock)

O executor monta o texto do orçamento localmente concatenando `businessContext` + `aiInstruction` do nó Fim. Não há chamada real a LLM — isso depende do backend.

#### Exemplo de Prompt a ser Gerado (Backend)

```
Você é o assistente de orçamentos da Total Électrique.

CONTEXTO DO NEGÓCIO:
{businessContext do nó Fim}

RESPOSTAS DO CLIENTE:
- Região: Laval
- Painel: 200A
- Espaços livres: Sim
- Spa: Não
- Tem borne: Não
- Local: Parede exterior
- Distância: 25 pés

INSTRUÇÃO:
{aiInstruction do nó Fim}

Gere o orçamento completo.
```

#### Fallback

Se a IA falhar (timeout, erro de API), o sistema gera um orçamento simplificado localmente com base em uma tabela de preços configurada pelo admin, sem detalhes em linguagem natural.

---

## 5. Arquitetura Técnica

### 5.1 Stack

| Camada | Tecnologia | Status |
|--------|-----------|--------|
| Frontend Builder | SvelteKit + Svelte 5 (runes) + @xyflow/svelte + Tailwind CSS 4 | Implementado |
| Frontend Cliente (Executor) | SvelteKit + Svelte 5 (mesma app) | Implementado (parcial) |
| Estilização | Tailwind CSS 4 + CSS custom properties para cores de nós | Implementado |
| Backend API | Python + FastAPI | Planejado |
| Banco de Dados | MongoDB (fluxos, respostas, orçamentos, users) | Planejado |
| IA | OpenAI GPT-4o / Anthropic Claude (configurável) | Planejado |
| Autenticação | JWT (admin) | Planejado |
| Deploy | Vercel / Azure | Planejado |
| Mock Mode | Dados em memória via flag `VITE_USE_MOCK` | Implementado |

### 5.2 Arquitetura do Frontend (Implementada)

```
src/
├── app.css                          # Tailwind imports + CSS vars de cores dos nós
├── app.html                         # HTML base SvelteKit
├── routes/
│   ├── +layout.svelte               # Layout raiz
│   ├── +page.svelte                 # Homepage com links para admin e demo
│   ├── admin/flows/
│   │   ├── +page.svelte             # Lista de fluxos
│   │   └── [id]/edit/+page.svelte   # Builder visual (canvas SvelteFlow)
│   └── q/[slug]/+page.svelte        # Executor do questionário (cliente)
├── lib/
│   ├── components/builder/
│   │   ├── nodes/
│   │   │   ├── StartNode.svelte     # Nó verde de início
│   │   │   ├── QuestionNode.svelte  # Nó azul de pergunta (9 tipos)
│   │   │   ├── MessageNode.svelte   # Nó cinza/vermelho de mensagem
│   │   │   └── EndNode.svelte       # Nó roxo de fim
│   │   └── panels/
│   │       ├── NodeToolbar.svelte   # Barra de ferramentas (adicionar nós)
│   │       └── NodeEditor.svelte    # Painel lateral de edição de propriedades
│   ├── config/
│   │   └── environment.ts           # VITE_USE_MOCK + VITE_API_URL
│   ├── dto/flows/
│   │   ├── types.ts                 # Interfaces: Flow, FlowNode, FlowEdge, FlowNodeData, etc.
│   │   ├── requests.ts              # SaveFlowRequest (validação + slug)
│   │   └── responses.ts             # FlowResponse (wrapper com getters)
│   ├── services/
│   │   └── flows.service.ts         # FlowsService (list, getById, getBySlug, save)
│   ├── data/
│   │   ├── repositories/
│   │   │   └── flows.repository.ts  # FlowsRepository (mock ou REST API)
│   │   └── mocks/
│   │       ├── index.ts
│   │       └── flows.ts             # Mock: "Devis Installation Borne" (12 perguntas, 4 fins)
│   └── stores/
│       └── flowBuilder.svelte.ts    # Store reativo (Svelte 5 $state) para o builder
```

### 5.3 Padrão de Camadas

```
Componente (Svelte) → Service → Repository → Mock Data | REST API
                                                         ↕
                                              environment.ts (VITE_USE_MOCK)
```

- **Service**: lógica de negócio e validação
- **Repository**: acesso a dados (mock ou fetch HTTP)
- **DTO**: tipagem forte com classes Request/Response
- **Store**: estado reativo do builder (Svelte 5 runes: `$state`, `$derived`)

### 5.4 Estrutura de Dados

#### FlowNodeData (TypeScript — implementado)

```typescript
type NodeType = 'start' | 'question' | 'message' | 'end';

type QuestionType = 'single_choice' | 'yes_no' | 'number' | 'text'
  | 'multiple_choice' | 'date' | 'rating' | 'dropdown' | 'photo';

interface FlowOption {
  id: string;
  label: string;
  value: string;
}

interface FlowNodeData {
  label: string;
  // Pergunta
  questionType?: QuestionType;
  options?: FlowOption[];
  required?: boolean;
  tooltip?: string;
  ratingMax?: number;
  // Mensagem
  message?: string;
  isSpecialist?: boolean;
  // Fim
  endType?: 'generate_quote' | 'specialist' | 'thank_you';
  businessContext?: string;
  aiInstruction?: string;
  specialistMessage?: string;
}
```

#### Fluxo (Flow) — formato persistido

```json
{
  "id": "string",
  "name": "Devis Installation Borne",
  "slug": "devis-installation-borne",
  "status": "draft | published | archived",
  "version": 1,
  "nodes": [
    {
      "id": "node_1",
      "type": "start | question | message | end",
      "position": { "x": 100, "y": 50 },
      "data": { "...FlowNodeData" }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "node_1",
      "target": "node_2",
      "sourceHandle": "opt_id (opcional, para roteamento por opção)"
    }
  ]
}
```

#### Resposta de Questionário — QuoteSession (Planejado, backend)

```json
{
  "_id": "ObjectId",
  "tenant_id": "string",
  "flow_id": "ObjectId",
  "flow_version": 3,
  "client": {
    "name": "Jean Dupont",
    "email": "jean@email.com",
    "phone": "+1 450-555-1234"
  },
  "answers": [
    { "node_id": "node_2", "question": "Région?", "value": "laval" },
    { "node_id": "node_3", "question": "Ampérage?", "value": "200" },
    { "node_id": "node_4", "question": "Spa?", "value": false }
  ],
  "result_type": "quote | specialist | thank_you",
  "quote_text": "DEVIS D'INSTALLATION...",
  "status": "pending",
  "created_at": "2026-03-10T15:00:00Z"
}
```

#### Lead de Suporte — SupportLead (Planejado, backend)

```json
{
  "_id": "ObjectId",
  "tenant_id": "string",
  "flow_id": "ObjectId",
  "client": { "name": "...", "email": "...", "phone": "..." },
  "answers": [],
  "specialist_node_id": "node_5",
  "reason": "Région non desservie",
  "status": "pending",
  "created_at": "2026-03-10T15:05:00Z"
}
```

---

## 6. Telas do Sistema

### 6.1 Área Admin

| # | Tela | Rota | Status |
|---|------|------|--------|
| A1 | Homepage | `/` | Implementado — links para admin e demo |
| A2 | Lista de Fluxos | `/admin/flows` | Implementado — cards com nome, status, slug, nós |
| A3 | Builder | `/admin/flows/[id]/edit` | Implementado — canvas completo com toolbar e editor lateral |
| A4 | Login | `/admin` | Planejado |
| A5 | Dashboard | `/admin/dashboard` | Planejado |
| A6 | Orçamentos | `/admin/quotes` | Planejado |
| A7 | Leads | `/admin/leads` | Planejado |
| A8 | Configurações | `/admin/settings` | Planejado |
| A9 | Preview | `/admin/flows/[id]/preview` | Planejado |

### 6.2 Área Cliente

| # | Tela | Rota | Status |
|---|------|------|--------|
| C1 | Formulário Inicial | `/q/[slug]` (fase form) | Implementado |
| C2 | Pergunta | `/q/[slug]` (fase questions) | Implementado (4 de 9 tipos) |
| C3 | Especialista | `/q/[slug]` (desvio) | Implementado |
| C4 | Orçamento | `/q/[slug]` (fase end) | Implementado (mock local, sem LLM) |

---

## 7. Regras de Negócio

1. **Um fluxo, um link.** Cada fluxo publicado gera uma URL única (`/q/devis-installation-borne`). O slug é gerado automaticamente a partir do nome.
2. **Versionamento.** Editar um fluxo publicado cria nova versão. Sessões em andamento continuam na versão anterior.
3. **tenant_id obrigatório.** Toda tabela e toda query inclui `tenant_id` — preparado para multi-tenant desde o dia 1.
4. **Fallback local.** Se a IA falhar, o orçamento é gerado com cálculo simplificado sem linguagem natural.
5. **Dados do cliente primeiro.** O fluxo sempre começa coletando nome, email e telefone.
6. **Respostas imutáveis.** Uma vez submetida, a sessão de respostas não pode ser editada pelo cliente.
7. **Nó Início único.** Cada fluxo tem exatamente um nó Início, que não pode ser deletado.
8. **Roteamento por opção.** Perguntas com opções (single_choice, multiple_choice, dropdown) roteiam via `sourceHandle` = ID da opção.
9. **Mock mode.** O frontend funciona 100% sem backend via flag `VITE_USE_MOCK=true`.
10. **SaveFlowRequest validado.** Nome obrigatório e pelo menos um nó para salvar.

---

## 8. Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| Tempo médio para completar questionário | < 3 minutos |
| Taxa de conclusão (iniciou → orçamento) | > 60% |
| Tempo de geração do orçamento (IA) | < 10 segundos |
| Orçamentos gerados por mês por cliente | > 50 |
| NPS do admin (facilidade do builder) | > 8 |

---

## 9. Fora de Escopo (v1)

- Pagamento online integrado ao orçamento
- Assinatura digital do orçamento
- App mobile nativo
- Integração com CRMs (Salesforce, HubSpot)
- Multi-idioma automático (admin configura no idioma que quiser)
- A/B testing de fluxos
- Webhooks para integração com sistemas externos

---

## 10. Roadmap

### Fase 1 — MVP Frontend (concluída)
- [x] Builder visual com @xyflow/svelte (nós: início, pergunta, mensagem, fim)
- [x] 9 tipos de pergunta no builder (single_choice, yes_no, number, text, multiple_choice, date, rating, dropdown, photo)
- [x] Painel lateral de edição de propriedades (NodeEditor)
- [x] Toolbar para adicionar nós
- [x] Handles de saída inteligentes por opção
- [x] Store reativo com Svelte 5 runes
- [x] Executor de questionário (4 tipos renderizados)
- [x] Navegação para trás no executor
- [x] Progress bar no executor
- [x] Lista de fluxos admin
- [x] Mock data completo (12 perguntas, 4 fins)
- [x] Camada de serviço/repositório com mock mode
- [x] Tailwind CSS 4 com CSS custom properties

### Fase 2 — MVP Backend + Integração
- [ ] Backend FastAPI (CRUD de fluxos, sessões, leads)
- [ ] MongoDB (persistência real)
- [ ] Integração frontend ↔ API REST (desligar mock mode)
- [ ] Geração de orçamento com LLM (OpenAI/Anthropic)
- [ ] Autenticação JWT (admin)
- [ ] Renderização dos 5 tipos de pergunta restantes no executor (multiple_choice, date, rating, dropdown, photo)
- [ ] Deploy inicial (Vercel frontend + Azure/Railway backend)

### Fase 3 — Polimento
- [ ] Dashboard com métricas
- [ ] Notificações por email
- [ ] Preview do fluxo
- [ ] Exportação PDF do orçamento
- [ ] Histórico de versões do fluxo
- [ ] Publicar/despublicar fluxo
- [ ] Drag & drop de nós do toolbar para o canvas

### Fase 4 — Escala
- [ ] Multi-tenant completo (onboarding self-service)
- [ ] Personalização visual (logo, cores, domínio customizado)
- [ ] Templates de fluxo pré-prontos por indústria
- [ ] API pública para integrações

---

## 11. Referência: Fluxo Demo (Total Électrique)

O sistema inclui um fluxo mock completo baseado na Total Électrique (instalação de bornes de carregamento EV no Quebec):

- **12 nós de pergunta** (P1 a P8, com variações):
  - Região, amperagem do painel, espaços livres, spa, borne existente, tipo de borne, local de instalação, distância do cabo
- **4 nós de fim**:
  - Especialista para regiões não atendidas
  - Especialista para painel cheio
  - Especialista para instalação interior
  - Geração de orçamento por IA (com businessContext detalhado incluindo preços)
- **Roteamento condicional** por região, espaço no painel e tipo de instalação
- **businessContext** com tabela de preços completa (bornes, instalação, cabeamento, deslocamento)

Este fluxo demo serve como referência funcional para validar o builder e o executor.
