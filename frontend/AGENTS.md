# Agentes Locais — FlowQuote

## Agente UI/UX — FlowQuote

### Missao
Garantir que toda interface do FlowQuote seja limpa, intuitiva e profissional.
O builder visual deve parecer um produto real (estilo Typeform, Pipedrive, Monday).

### Principios de Design FlowQuote

1. **Canvas limpo** — fundo claro com grid sutil, nós com sombras suaves e bordas arredondadas
2. **Cores com significado** — cada tipo de nó tem cor fixa:
   - Pergunta: azul (`blue-500`)
   - Mensagem: cinza (`gray-500`)
   - Condição: amarelo (`amber-500`)
   - Fim: roxo (`purple-500`)
   - Início: verde (`green-500`)
3. **Toolbar clara** — ícones + texto, agrupados por função
4. **Painel lateral** — aparece à direita ao clicar num nó, com transição suave
5. **Tipografia** — Inter ou system sans-serif, hierarquia clara (título > subtítulo > body > caption)
6. **Espaçamento** — padding generoso, nunca apertado
7. **Feedback visual** — nó selecionado tem ring/glow, hover muda borda, save tem toast
8. **Responsivo** — builder funciona em desktop (min 1024px), executor funciona em mobile
9. **Acessibilidade** — contraste mínimo 4.5:1, focus visible, labels em inputs

### Executor (formulário do cliente)
- Card centralizado, max-width 480px
- Progress bar no topo
- Transições suaves entre perguntas
- Botões grandes e fáceis de clicar no mobile
- Cores neutras — o conteúdo é o foco

### Anti-patterns (NUNCA fazer)
- Gradientes exagerados nos nós
- Ícones demais sem texto
- Animações que atrasam a interação
- Texto cinza claro em fundo branco (baixo contraste)
- Modais para edição (usar painel lateral)
