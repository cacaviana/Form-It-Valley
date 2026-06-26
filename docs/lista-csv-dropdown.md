# Lista suspensa (dropdown) e o CSV de preços

> Resposta à dúvida da Laura no documento "Correções Sistema Calenda": o que é "Liste déroulante" / Lista suspensa e o que tem a ver com o CSV.

## O que é a Lista suspensa

É um **tipo de pergunta** no builder, equivalente a um `<select>` HTML. O lead vê um campo do tipo "selecione uma opção" com uma seta — abre, escolhe uma das opções configuradas, fecha.

Use quando:
- A pergunta tem **muitas opções** (5+). Botões empilhados ficariam grandes; o dropdown deixa o formulário compacto.
- A opção é uma escolha simples de um valor (estado, cidade, marca, modelo, etc).

Para 2 a 4 opções, prefira **Escolha única** (botões) — visualmente é mais rápido pro lead.

## Como adicionar opções

Cada opção do dropdown é configurada manualmente no painel do nó: clique em "+ Adicionar", digite o texto, e pode vincular a um produto do catálogo (CSV).

Cada opção também cria uma **saída do fluxo** — você pode conectar cada opção a um próximo nó diferente, fazendo o lead seguir caminhos distintos no fluxo conforme escolhe.

## Onde entra o CSV de preços

O CSV não cria as opções automaticamente. Ele serve para **vincular cada opção a um produto do catálogo**, e isso só é útil quando o fluxo termina em "Gerar orçamento via IA".

Sem CSV vinculado:
- A IA gera o orçamento usando livre interpretação do texto da opção. Pode acertar, pode errar.

Com CSV vinculado:
- Cada opção tem um produto definido com nome, preço, unidade e categoria.
- A IA usa esses valores exatos. Resultado consistente, sem alucinação.

Quando o flow é **agendamento** (sem geração de orçamento), o CSV é irrelevante — pode ignorar.

## Fluxo prático

1. Crie uma pergunta tipo "Lista suspensa".
2. Digite o título (ex: "Em qual estado você mora?").
3. Adicione as opções (SP, RJ, MG, ...).
4. (Opcional) Se o flow gera orçamento e o estado define preço diferente, suba um CSV com `estado,preco` e vincule cada opção a uma linha.
5. Conecte a saída da pergunta ao próximo nó (uma saída só, ou uma por opção se quiser bifurcar).

## Diferença entre Lista suspensa, Múltipla escolha e Escolha única

| Tipo                | Visual                          | Quantas opções o lead escolhe |
|---------------------|---------------------------------|-------------------------------|
| Escolha única       | Botões empilhados               | 1                             |
| Lista suspensa      | Dropdown `<select>`             | 1                             |
| Múltipla escolha    | Botões empilhados com checkbox  | Várias                        |

O **Escolha única** e a **Lista suspensa** entregam a mesma resposta — a diferença é só visual. Use o dropdown quando tem muita opção pra não poluir a tela.
