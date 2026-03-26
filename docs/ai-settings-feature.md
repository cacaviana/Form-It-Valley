# Configurações de IA — Feature de Seleção de Modelo

## O que foi construído

Uma página de configurações no admin (`/admin/settings`) que permite trocar o provedor e modelo
de IA sem tocar no `.env` e sem reiniciar o servidor. A escolha fica persistida no MongoDB.

---

## Arquivos criados/modificados

### Backend

**`backend/routers/settings.py`** ← novo
- `GET /api/settings/ai` — retorna provider atual, model atual e lista de modelos disponíveis
- `PUT /api/settings/ai` — salva a escolha no MongoDB (collection `settings`, doc `ai_settings`)
- Fallback: se não houver doc no MongoDB, usa valores do `.env`

**`backend/config/settings.py`** ← modificado
- Adicionado campo `openai_base_url: Optional[str]` para suporte a provedores compatíveis
  com OpenAI (ex: DeepSeek em `https://api.deepseek.com`)

**`backend/main.py`** ← modificado
- Registra o novo `settings_router`

**`backend/routers/agent.py`** ← modificado
- `/api/agent/info` era síncrono e importava o `quote_agent` global (que foi removido)
- Agora usa `await _get_model_name()` e a constante `_AGENT_INSTRUCTIONS`

**`backend/services/quote_generator.py`** ← modificado (refatoração significativa)

Antes: `quote_agent` era uma instância global criada no startup com modelo fixo do `.env`.
Depois: o agente é criado dinamicamente por modelo, com cache.

Mudanças:
1. `_get_model_name()` virou `async` — busca o modelo no MongoDB via `get_ai_config()`
2. Funções `build_context` e `validate_quote` perderam os decorators `@quote_agent.*`
   porque o agente global foi removido
3. Nova função `_get_or_build_agent(model_name)` — cria Agent + registra as funções,
   com cache por `model_name` para não recriar a cada request
4. `_AGENT_INSTRUCTIONS` virou constante de módulo (estava inline no constructor do Agent)
5. `QuoteGenerator.generate()` chama `await _get_model_name()` + `_get_or_build_agent()`
   a cada geração — sempre usa o modelo mais recente salvo no DB

### Frontend

**`frontend/src/routes/api/settings/+server.ts`** ← novo
- Proxy SvelteKit: GET e PUT redirecionam para `http://localhost:8001/api/settings/ai`

**`frontend/src/routes/admin/settings/+page.svelte`** ← novo
- Carrega configuração atual no `onMount`
- Dois seletores visuais: provedor (Anthropic / OpenAI) + modelo dentro do provedor
- Ao mudar provedor, seleciona automaticamente o primeiro modelo disponível
- Botão "Salvar" → PUT para o backend
- Feedback visual "Salvo! O próximo orçamento usará este modelo."

**`frontend/src/routes/admin/flows/+page.svelte`** ← modificado
- Adicionado botão "IA" (ícone de engrenagem) no header → navega para `/admin/settings`

---

## Modelos disponíveis

```
Anthropic:
  - claude-sonnet-4-20250514  →  Claude Sonnet 4
  - claude-opus-4-6           →  Claude Opus 4.6

OpenAI:
  - gpt-4o                    →  GPT-4o
  - gpt-4.5-preview           →  GPT-4.5
```

Lista definida em `backend/routers/settings.py` → constante `MODELS`.

---

## Como a troca de modelo funciona em runtime

```
Admin acessa /admin/settings
        ↓
Seleciona "OpenAI → GPT-4o" e clica Salvar
        ↓
PUT /api/settings → Python backend → upsert em MongoDB{_id: "ai_settings"}
        ↓
Próximo cliente preenche formulário e chega ao endpoint de geração
        ↓
QuoteGenerator.generate():
    model_name = await _get_model_name()
    # → lê MongoDB → retorna "openai:gpt-4o"
    agent = _get_or_build_agent("openai:gpt-4o")
    # → cache hit se já foi criado antes, senão cria novo Agent
    result = await agent.run(...)
```

O `.env` continua sendo o fallback. O MongoDB tem prioridade.

---

## Cache de agentes

O `_agent_cache: dict[str, Agent]` guarda instâncias por `model_name` (ex: `"anthropic:claude-sonnet-4-20250514"`).

- Se o admin troca de Sonnet para GPT-4o e depois volta para Sonnet: ambos estão em cache,
  sem overhead de recriação.
- O cache vive durante o processo uvicorn. Reiniciar o servidor limpa o cache (sem problema,
  pois a criação do Agent é barata).

---

## Por que o agente global foi removido

O PydanticAI `Agent` recebe o `model` no construtor. Não tem como trocar o modelo de um Agent
depois de criado. A única forma de suportar troca dinâmica é criar novos agentes.

Os decorators `@quote_agent.system_prompt` e `@quote_agent.output_validator` estavam presos
à instância global. Após a refatoração, as mesmas funções são registradas em cada nova
instância via chamada explícita:

```python
agent.system_prompt(build_context)
agent.output_validator(validate_quote)
```
