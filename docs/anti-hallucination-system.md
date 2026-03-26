# Sistema Anti-Alucinação — FlowQuote

## O que é

O FlowQuote é um SaaS onde admins constroem fluxos de questionário (tipo "wizard") e clientes
respondem para receber um orçamento gerado por IA. O problema central: a IA pode **alucinar**
preços ou substituir produtos que o cliente escolheu por produtos parecidos do catálogo.

Este documento descreve o sistema de 3 camadas construído para eliminar esse problema.

---

## O problema de alucinação neste contexto

O admin carrega um CSV de produtos/preços (o catálogo). O cliente responde perguntas e escolhe
opções. A IA recebe as respostas e gera o orçamento.

Dois tipos de alucinação possíveis:

1. **Substituição de nome**: cliente escolheu "Camera 4K Ultra HD" (ausente do CSV) → IA escreve
   "Camera IP 4MP" (produto similar que existe no CSV).

2. **Invenção de preço**: item ausente → IA inventa um preço aproximado baseado em produto similar.

A regra de negócio correta: se o item não existe no catálogo, deve aparecer como
`"(prix a consulter)"` com preço zero.

---

## Arquitetura: 3 camadas

### Camada 1 — Classificação no Prompt (`build_context`)

**Arquivo:** `backend/services/quote_generator.py` → função `build_context`

Antes de enviar à IA, cada resposta do cliente é classificada em um de três buckets:

```
PRODUTOS CONFIRMADOS       → existem no CSV com preço exato
PRODUTOS AUSENTES          → cliente escolheu, mas não existe no CSV
OUTRAS RESPOSTAS           → contexto puro (região, nome, amperagem, etc.)
```

O prompt enviado à IA inclui instruções explícitas por bucket:
- Confirmados: "copie com o preço exato, não altere nada"
- Ausentes: "inclua com `(prix a consulter)`, INTERDIT de renomear"
- Outros: "use como contexto, nunca como item de linha"

**Lógica de classificação (prioridade):**
1. Admin mapeou explicitamente via `catalogProduct` no builder → usa esse mapeamento
2. O `value` da resposta bate exatamente com um produto do CSV → confirmado
3. Sem match → contexto puro ou ausente

---

### Camada 2 — Matching por Keywords (`_find_catalog_match`)

**Arquivo:** `backend/services/quote_generator.py` → função `_find_catalog_match`

Usada para classificar itens e depois no validador. Regras:

- Tokeniza nome do produto (lowercase, split por espaço/pontuação)
- Só aceita match se **≥ 2 tokens significativos** coincidem
- Token é "significativo" se: `len > 3` OU `len >= 2 e contém dígito`
  - Exemplos: "borne" (5 chars ✓), "32a" (dígito ✓), "de" (2 chars, sem dígito ✗)
- Isso previne que "App mobile iOS" e "App mobile hibrido" se confundam via token "mobile" sozinho

---

### Camada 3 — Validador Pós-IA (`validate_quote`)

**Arquivo:** `backend/services/quote_generator.py` → função `validate_quote`

Roda depois que a IA retorna o JSON. Três sub-etapas:

**3a — Força preço do CSV**
Para cada item que a IA retornou, tenta encontrar no catálogo via `_find_catalog_match`.
Se encontrar: substitui `unit_price` pelo preço do CSV (a IA não pode inventar preço).

**3b — Limita quantidade de itens adicionados pela IA**
A IA pode adicionar produtos complementares (upsell). Mas se o item não foi mencionado
explicitamente pelo cliente, força `quantity = 1`. Impede que a IA "sugira" 10 unidades de algo.

**3c — Re-injeta produtos confirmados omitidos**
Modelos mais conservadores (ex: Claude Haiku) às vezes marcam tudo como "A consulter".
O validador verifica se todos os produtos classificados como CONFIRMADOS na Camada 1
estão presentes no resultado. Se algum foi omitido ou marcado errado, re-injeta com
preço e quantidade corretos.

---

## Resultados por modelo testado

| Modelo | Resultado | Observação |
|---|---|---|
| Claude Sonnet 4 | ✅ 2/2 | Referência. Segue todas as regras. |
| GPT-4o | ✅ 2/2 | Passa com as 3 camadas ativas. |
| GPT-4o-mini | ❌ 0/2 | Substitui nomes e inventa preços. Não corrigível por prompt. |
| Claude Haiku 4.5 | ⚠️ 2/2 (com 3c) | Muito conservador: marcava tudo como "A consulter". Layer 3c corrige. |
| deepseek-chat | ⚠️ 1/2 | Passa em fluxos simples. Falha adicionando itens de catálogo como "complementares" quando deveria não tocar na categoria. |
| deepseek-reasoner | ❌ Incompatível | Não suporta `tool_choice` — o PydanticAI precisa disso para output estruturado. |

---

## Fluxo de dados completo

```
Cliente responde questionário
        ↓
SvelteKit /q/[slug] coleta respostas
        ↓
POST /api/submissions (SvelteKit → MongoDB + Python)
        ↓
Python backend: SubmissionService.generate_quote()
        ↓
QuoteGenerator.generate()
        ↓
[Camada 1] build_context() — classifica respostas e monta prompt
        ↓
PydanticAI → Modelo de IA (Sonnet / GPT-4o / etc.)
        ↓
IA retorna QuoteOutput (JSON estruturado via tool_choice)
        ↓
[Camada 3] validate_quote() — força preços CSV, limita qty, re-injeta confirmados
        ↓
Resultado salvo em MongoDB + exibido ao cliente
```

---

## Testes automatizados

**Arquivos:** `frontend/tests/automacao-comercial.spec.ts`, `frontend/tests/dev-software.spec.ts`

Cada teste:
1. Seleciona intencionalmente opções **ausentes** do CSV ("armadilhas de alucinação")
2. Seleciona opções **presentes** no CSV para validar preços corretos
3. Verifica que nenhum nome de produto similar aparece no resultado
4. Verifica que itens ausentes aparecem como "A consulter"
5. Verifica que itens presentes têm preço real

Exemplo de armadilha no teste `automacao-comercial`:
- CSV tem: "Camera IP 4MP", "Camera IP 8MP"
- Cliente escolhe: "Camera 4K Ultra HD" (não existe no CSV)
- Teste verifica: resultado NÃO contém "camera ip 4mp" nem "camera ip 8mp"

---

## Configuração de modelos

**Arquivo:** `backend/config/settings.py`

Variáveis de ambiente:
```
AI_PROVIDER=anthropic        # ou "openai"
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=...          # opcional — para provedores compatíveis como DeepSeek
```

O admin pode trocar o modelo via interface em `/admin/settings` sem precisar reiniciar o servidor
(a escolha fica salva no MongoDB, com prioridade sobre o `.env`).
