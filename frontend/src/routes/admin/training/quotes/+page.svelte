<script lang="ts">
  import { goto } from '$app/navigation';
  let lang = $state<'pt' | 'fr' | 'en' | 'es'>('pt');
  let expandedFaq = $state<number | null>(null);

  function toggleFaq(i: number) { expandedFaq = expandedFaq === i ? null : i; }

  // ── i18n ──
  const i: Record<string, Record<string, string>> = {
    back: { pt: 'Voltar ao painel', fr: 'Retour au panneau', en: 'Back to dashboard', es: 'Volver al panel' },
    hero1: { pt: 'Bem-vindo ao FlowQuote!', fr: 'Bienvenue sur FlowQuote !', en: 'Welcome to FlowQuote!', es: '¡Bienvenido a FlowQuote!' },
    hero2: { pt: 'Vamos te ensinar a criar seu primeiro orçamento automático em 5 minutos.', fr: 'Nous allons vous apprendre à créer votre premier devis automatique en 5 minutes.', en: 'We\'ll teach you to create your first automatic quote in 5 minutes.', es: 'Te enseñaremos a crear tu primer presupuesto automático en 5 minutos.' },
    hero3: { pt: 'Não se preocupe, é super simples. Vamos juntos!', fr: 'Ne vous inquiétez pas, c\'est très simple. Allons-y ensemble !', en: 'Don\'t worry, it\'s super simple. Let\'s go together!', es: 'No te preocupes, es súper simple. ¡Vamos juntos!' },

    whatTitle: { pt: 'O que é o FlowQuote?', fr: 'Qu\'est-ce que FlowQuote ?', en: 'What is FlowQuote?', es: '¿Qué es FlowQuote?' },
    whatP1: { pt: 'Sabe quando um cliente te pede um orçamento e você precisa fazer várias perguntas antes de dar o preço? O FlowQuote faz isso por você — automaticamente.', fr: 'Vous savez quand un client vous demande un devis et vous devez poser plusieurs questions avant de donner le prix ? FlowQuote fait ça pour vous — automatiquement.', en: 'You know when a client asks for a quote and you need to ask several questions before giving a price? FlowQuote does this for you — automatically.', es: '¿Sabes cuando un cliente te pide un presupuesto y necesitas hacer varias preguntas antes de dar el precio? FlowQuote hace eso por ti — automáticamente.' },
    whatP2: { pt: 'Você monta as perguntas uma vez, e seus clientes acessam um link, respondem, e recebem o orçamento na hora. Funciona 24 horas, 7 dias por semana.', fr: 'Vous créez les questions une fois, et vos clients accèdent à un lien, répondent, et reçoivent le devis instantanément. Fonctionne 24/7.', en: 'You set up the questions once, and your clients access a link, answer, and get the quote instantly. Works 24/7.', es: 'Montas las preguntas una vez, y tus clientes acceden a un enlace, responden, y reciben el presupuesto al instante. Funciona 24/7.' },

    howTitle: { pt: 'Como funciona? (Visão geral)', fr: 'Comment ça marche ? (Aperçu)', en: 'How does it work? (Overview)', es: '¿Cómo funciona? (Visión general)' },
    howStep1: { pt: 'Você cria as perguntas no editor visual', fr: 'Vous créez les questions dans l\'éditeur visuel', en: 'You create the questions in the visual editor', es: 'Usted crea las preguntas en el editor visual' },
    howStep2: { pt: 'Carrega sua tabela de preços (CSV)', fr: 'Charge votre liste de prix (CSV)', en: 'Upload your price list (CSV)', es: 'Carga su tabla de precios (CSV)' },
    howStep3: { pt: 'Vincula cada pergunta ao produto certo', fr: 'Lie chaque question au bon produit', en: 'Link each question to the right product', es: 'Vincula cada pregunta al producto correcto' },
    howStep4: { pt: 'Publica e compartilha o link', fr: 'Publie et partage le lien', en: 'Publish and share the link', es: 'Publica y comparte el enlace' },
    howStep5: { pt: 'O cliente responde e recebe o orçamento!', fr: 'Le client répond et reçoit le devis !', en: 'The client answers and gets the quote!', es: '¡El cliente responde y recibe el presupuesto!' },

    guideTitle: { pt: 'Passo a Passo: Criando seu Primeiro Orçamento', fr: 'Étape par Étape : Créer Votre Premier Devis', en: 'Step by Step: Creating Your First Quote', es: 'Paso a Paso: Creando su Primer Presupuesto' },

    step1t: { pt: 'Passo 1: Crie um novo fluxo', fr: 'Étape 1 : Créer un nouveau flux', en: 'Step 1: Create a new flow', es: 'Paso 1: Cree un nuevo flujo' },
    step1d: { pt: 'No painel admin, clique no botão azul:', fr: 'Dans le panneau admin, cliquez sur le bouton bleu :', en: 'In the admin panel, click the blue button:', es: 'En el panel admin, haga clic en el botón azul:' },

    step2t: { pt: 'Passo 2: Monte as perguntas arrastando blocos', fr: 'Étape 2 : Créez les questions en glissant des blocs', en: 'Step 2: Build questions by dragging blocks', es: 'Paso 2: Monte las preguntas arrastrando bloques' },
    step2d: { pt: 'O editor visual funciona assim: você arrasta blocos e conecta com setas. Cada bloco é um passo do questionário.', fr: 'L\'éditeur visuel fonctionne ainsi : vous glissez des blocs et les connectez avec des flèches. Chaque bloc est une étape du questionnaire.', en: 'The visual editor works like this: you drag blocks and connect them with arrows. Each block is a step in the questionnaire.', es: 'El editor visual funciona así: usted arrastra bloques y los conecta con flechas. Cada bloque es un paso del cuestionario.' },

    step3t: { pt: 'Passo 3: Carregue sua tabela de preços (CSV)', fr: 'Étape 3 : Chargez votre liste de prix (CSV)', en: 'Step 3: Upload your price list (CSV)', es: 'Paso 3: Cargue su tabla de precios (CSV)' },
    step3d: { pt: 'No nó final (roxo), cole ou carregue sua tabela. Pode ser simples assim:', fr: 'Dans le nœud final (violet), collez ou chargez votre liste. C\'est aussi simple que :', en: 'In the end node (purple), paste or upload your table. It can be as simple as:', es: 'En el nodo final (morado), pegue o cargue su tabla. Puede ser tan simple como:' },

    step4t: { pt: 'Passo 4: Vincule as perguntas aos produtos', fr: 'Étape 4 : Liez les questions aux produits', en: 'Step 4: Link questions to products', es: 'Paso 4: Vincule las preguntas a los productos' },
    step4d: { pt: 'Essa é a parte mais importante! Clique em cada pergunta e vincule cada opção ao produto do CSV.', fr: 'C\'est la partie la plus importante ! Cliquez sur chaque question et liez chaque option au produit du CSV.', en: 'This is the most important part! Click each question and link each option to the CSV product.', es: '¡Esta es la parte más importante! Haga clic en cada pregunta y vincule cada opción al producto del CSV.' },

    step5t: { pt: 'Passo 5: Salve e publique!', fr: 'Étape 5 : Enregistrez et publiez !', en: 'Step 5: Save and publish!', es: 'Paso 5: ¡Guarde y publique!' },
    step5d: { pt: 'Clique em "Salvar", mude o status para "Publicado", e compartilhe o link com seus clientes!', fr: 'Cliquez sur "Enregistrer", changez le statut en "Publié", et partagez le lien avec vos clients !', en: 'Click "Save", change the status to "Published", and share the link with your clients!', es: '¡Haga clic en "Guardar", cambie el estado a "Publicado", y comparta el enlace con sus clientes!' },

    typesTitle: { pt: 'Entenda os Dois Tipos de Pergunta', fr: 'Comprendre les Deux Types de Questions', en: 'Understand the Two Types of Questions', es: 'Entienda los Dos Tipos de Pregunta' },
    typesIntro: { pt: 'Esse é o segredo para um orçamento perfeito. Existem perguntas que geram itens no orçamento e perguntas que só dão contexto.', fr: 'C\'est le secret d\'un devis parfait. Il y a des questions qui génèrent des articles et des questions qui donnent juste du contexte.', en: 'This is the secret to a perfect quote. There are questions that generate items and questions that just give context.', es: 'Este es el secreto para un presupuesto perfecto. Hay preguntas que generan ítems y preguntas que solo dan contexto.' },

    ctxTitle: { pt: 'Pergunta de CONTEXTO', fr: 'Question de CONTEXTE', en: 'CONTEXT Question', es: 'Pregunta de CONTEXTO' },
    ctxWhen: { pt: 'Use quando você quer entender a situação do cliente, mas a resposta NÃO gera um item no orçamento.', fr: 'Utilisez quand vous voulez comprendre la situation du client, mais la réponse NE génère PAS un article dans le devis.', en: 'Use when you want to understand the client\'s situation, but the answer does NOT generate an item in the quote.', es: 'Use cuando quiera entender la situación del cliente, pero la respuesta NO genera un ítem en el presupuesto.' },
    ctxNeedsCsv: { pt: 'Precisa vincular ao CSV?', fr: 'Besoin de lier au CSV ?', en: 'Need to link to CSV?', es: '¿Necesita vincular al CSV?' },
    ctxNo: { pt: 'NÃO', fr: 'NON', en: 'NO', es: 'NO' },

    quoteTitle: { pt: 'Pergunta de ORÇAMENTO', fr: 'Question de DEVIS', en: 'QUOTE Question', es: 'Pregunta de PRESUPUESTO' },
    quoteWhen: { pt: 'Use quando a resposta do cliente DETERMINA qual produto entra no orçamento e o preço.', fr: 'Utilisez quand la réponse du client DÉTERMINE quel produit entre dans le devis et le prix.', en: 'Use when the client\'s answer DETERMINES which product goes in the quote and the price.', es: 'Use cuando la respuesta del cliente DETERMINA qué producto entra en el presupuesto y el precio.' },
    quoteYes: { pt: 'SIM, OBRIGATÓRIO!', fr: 'OUI, OBLIGATOIRE !', en: 'YES, MANDATORY!', es: '¡SÍ, OBLIGATORIO!' },

    rulesTitle: { pt: 'As 2 Regras de Ouro', fr: 'Les 2 Règles d\'Or', en: 'The 2 Golden Rules', es: 'Las 2 Reglas de Oro' },
    rule1: { pt: 'A IA só calcula preço se o produto estiver no CSV', fr: 'L\'IA ne calcule le prix que si le produit est dans le CSV', en: 'AI only calculates price if the product is in the CSV', es: 'La IA solo calcula precio si el producto está en el CSV' },
    rule1d: { pt: 'Sem CSV = sem preço. O item vai aparecer como "A consultar". Sempre carregue sua tabela!', fr: 'Sans CSV = sans prix. L\'article apparaîtra comme "À consulter". Chargez toujours votre liste !', en: 'No CSV = no price. The item will show as "To be quoted". Always upload your table!', es: 'Sin CSV = sin precio. El ítem aparecerá como "A consultar". ¡Siempre cargue su tabla!' },
    rule2: { pt: 'A IA só inclui o produto se a pergunta estiver vinculada a ele', fr: 'L\'IA n\'inclut le produit que si la question est liée à lui', en: 'AI only includes the product if the question is linked to it', es: 'La IA solo incluye el producto si la pregunta está vinculada a él' },
    rule2d: { pt: 'O produto pode estar no CSV, mas se a opção da pergunta não estiver vinculada, a IA não sabe que o cliente escolheu aquilo.', fr: 'Le produit peut être dans le CSV, mais si l\'option de la question n\'est pas liée, l\'IA ne sait pas que le client a choisi cela.', en: 'The product may be in the CSV, but if the question option isn\'t linked, the AI doesn\'t know the client chose it.', es: 'El producto puede estar en el CSV, pero si la opción de la pregunta no está vinculada, la IA no sabe que el cliente eligió eso.' },
    formula: { pt: 'CSV + Vínculo = Orçamento Perfeito', fr: 'CSV + Lien = Devis Parfait', en: 'CSV + Link = Perfect Quote', es: 'CSV + Vínculo = Presupuesto Perfecto' },

    faqTitle: { pt: 'Perguntas Frequentes', fr: 'Questions Fréquentes', en: 'FAQ', es: 'Preguntas Frecuentes' },
    faq1q: { pt: 'E se eu não tiver um CSV?', fr: 'Et si je n\'ai pas de CSV ?', en: 'What if I don\'t have a CSV?', es: '¿Y si no tengo un CSV?' },
    faq1a: { pt: 'Você pode digitar a tabela de preços diretamente no campo "Tabela de preços" do nó final. Coloque um produto por linha com o preço. Exemplo: "Tomada 110V: R$25"', fr: 'Vous pouvez taper la liste de prix directement dans le champ "Liste de prix" du nœud final. Mettez un produit par ligne avec le prix. Exemple : "Prise 110V : 25$"', en: 'You can type the price list directly in the "Price table" field of the end node. Put one product per line with the price. Example: "110V Outlet: $25"', es: 'Puede escribir la tabla de precios directamente en el campo "Tabla de precios" del nodo final. Ponga un producto por línea con el precio. Ejemplo: "Toma 110V: $25"' },
    faq2q: { pt: 'A IA pode errar o orçamento?', fr: 'L\'IA peut-elle se tromper dans le devis ?', en: 'Can the AI get the quote wrong?', es: '¿La IA puede equivocarse en el presupuesto?' },
    faq2a: { pt: 'Sim, IAs podem cometer erros. Por isso, quanto melhor suas regras de negócio e mais claro o CSV, melhor o resultado. Sempre revise antes de enviar ao cliente final.', fr: 'Oui, les IAs peuvent se tromper. C\'est pourquoi, plus vos règles métier sont claires et plus le CSV est clair, meilleur sera le résultat. Vérifiez toujours avant d\'envoyer au client.', en: 'Yes, AIs can make mistakes. That\'s why, the better your business rules and the clearer the CSV, the better the result. Always review before sending to the final client.', es: 'Sí, las IAs pueden cometer errores. Por eso, cuanto mejores sus reglas de negocio y más claro el CSV, mejor el resultado. Siempre revise antes de enviar al cliente final.' },
    faq3q: { pt: 'Posso ter mais de um fluxo?', fr: 'Puis-je avoir plus d\'un flux ?', en: 'Can I have more than one flow?', es: '¿Puedo tener más de un flujo?' },
    faq3a: { pt: 'Sim! Crie quantos fluxos quiser. Um para cada serviço, produto ou público diferente.', fr: 'Oui ! Créez autant de flux que vous voulez. Un pour chaque service, produit ou public différent.', en: 'Yes! Create as many flows as you want. One for each service, product or different audience.', es: '¡Sí! Cree cuantos flujos quiera. Uno para cada servicio, producto o público diferente.' },

    cta: { pt: 'Criar Meu Primeiro Orçamento', fr: 'Créer Mon Premier Devis', en: 'Create My First Quote', es: 'Crear Mi Primer Presupuesto' },
  };
  function _(k: string): string { return i[k]?.[lang] || i[k]?.['pt'] || k; }
</script>

<div class="min-h-screen bg-white">
  <!-- Sticky header -->
  <header class="bg-white/80 backdrop-blur-md border-b sticky top-0 z-10">
    <div class="max-w-3xl mx-auto px-6 py-3 flex items-center justify-between">
      <button onclick={() => goto('/admin/flows')} class="text-sm text-gray-500 hover:text-gray-800 cursor-pointer flex items-center gap-1.5">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
        {_('back')}
      </button>
      <div class="flex gap-0.5 bg-gray-100 rounded-full p-0.5">
        {#each (['pt', 'fr', 'en', 'es'] as const) as l}
          <button onclick={() => lang = l} class="w-9 h-8 rounded-full text-xs font-bold uppercase cursor-pointer transition-all {lang === l ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-400 hover:text-gray-600'}">{l}</button>
        {/each}
      </div>
    </div>
  </header>

  <main class="max-w-3xl mx-auto px-6">

    <!-- ══════ HERO ══════ -->
    <section class="py-16 text-center">
      <div class="w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/30">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" /></svg>
      </div>
      <h1 class="text-4xl font-black text-gray-900 mb-3">{_('hero1')}</h1>
      <p class="text-lg text-gray-600 mb-2">{_('hero2')}</p>
      <p class="text-base text-gray-400">{_('hero3')}</p>
    </section>

    <!-- ══════ O QUE É ══════ -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-blue-600 uppercase tracking-widest mb-2">01</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-4">{_('whatTitle')}</h3>
      <div class="bg-blue-50 rounded-2xl p-6 space-y-4">
        <p class="text-gray-700 leading-relaxed">{_('whatP1')}</p>
        <p class="text-gray-600 leading-relaxed">{_('whatP2')}</p>
      </div>

      <!-- Mockup: what client sees -->
      <div class="mt-6 border-2 border-gray-200 rounded-2xl overflow-hidden shadow-xl">
        <div class="bg-gray-100 px-4 py-2 flex items-center gap-2 border-b">
          <div class="flex gap-1.5"><div class="w-3 h-3 rounded-full bg-red-400"></div><div class="w-3 h-3 rounded-full bg-yellow-400"></div><div class="w-3 h-3 rounded-full bg-green-400"></div></div>
          <div class="flex-1 bg-white rounded-md px-3 py-1 text-xs text-gray-400 text-center">seusite.com/q/orcamento-eletrico</div>
        </div>
        <div class="bg-gradient-to-b from-gray-50 to-gray-100 p-8 flex justify-center">
          <div class="bg-white rounded-2xl shadow-lg border max-w-sm w-full p-6">
            <h4 class="text-lg font-bold text-gray-900 mb-1">{lang === 'pt' ? 'Orçamento Elétrico' : lang === 'fr' ? 'Devis Électrique' : lang === 'en' ? 'Electrical Quote' : 'Presupuesto Eléctrico'}</h4>
            <p class="text-xs text-gray-400 mb-5">{lang === 'pt' ? 'Responda e receba seu orçamento na hora' : lang === 'fr' ? 'Répondez et recevez votre devis instantanément' : lang === 'en' ? 'Answer and get your quote instantly' : 'Responda y reciba su presupuesto al instante'}</p>
            <div class="space-y-3 mb-5">
              <div class="bg-gray-50 rounded-lg px-3 py-2.5 border text-sm text-gray-700">{lang === 'pt' ? 'João Silva' : 'Jean Dupont'}</div>
              <div class="bg-gray-50 rounded-lg px-3 py-2.5 border text-sm text-gray-700">joao@email.com</div>
              <div class="bg-gray-50 rounded-lg px-3 py-2.5 border text-sm text-gray-400">(11) 99999-0000</div>
            </div>
            <div class="bg-blue-600 text-white text-center py-2.5 rounded-lg text-sm font-semibold">{lang === 'pt' ? 'Começar' : lang === 'fr' ? 'Commencer' : lang === 'en' ? 'Start' : 'Empezar'}</div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-2 border-t text-center">
          <span class="text-xs text-gray-400">{lang === 'pt' ? '↑ Isso é o que seu cliente vê quando acessa o link' : lang === 'fr' ? '↑ C\'est ce que votre client voit en accédant au lien' : lang === 'en' ? '↑ This is what your client sees when they access the link' : '↑ Esto es lo que su cliente ve al acceder al enlace'}</span>
        </div>
      </div>
    </section>

    <!-- ══════ COMO FUNCIONA ══════ -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-blue-600 uppercase tracking-widest mb-2">02</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-6">{_('howTitle')}</h3>
      <div class="relative">
        {#each [
          { t: 'howStep1', emoji: '🎨', color: 'blue' },
          { t: 'howStep2', emoji: '📊', color: 'green' },
          { t: 'howStep3', emoji: '🔗', color: 'purple' },
          { t: 'howStep4', emoji: '🚀', color: 'amber' },
          { t: 'howStep5', emoji: '✅', color: 'emerald' }
        ] as step, idx}
          <div class="flex gap-4 mb-0">
            <div class="flex flex-col items-center">
              <div class="w-12 h-12 rounded-2xl bg-{step.color}-100 flex items-center justify-center text-xl flex-shrink-0">{step.emoji}</div>
              {#if idx < 4}<div class="w-0.5 h-6 bg-gray-200"></div>{/if}
            </div>
            <div class="pt-2.5 pb-4">
              <p class="text-base font-semibold text-gray-800">{_(step.t)}</p>
            </div>
          </div>
        {/each}
      </div>
    </section>

    <!-- ══════ PASSO A PASSO ══════ -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-blue-600 uppercase tracking-widest mb-2">03</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-8">{_('guideTitle')}</h3>

      <!-- Step 1: New flow -->
      <div class="mb-12">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-black">1</div>
          <h4 class="text-lg font-bold text-gray-900">{_('step1t')}</h4>
        </div>
        <p class="text-gray-600 mb-4 ml-12">{_('step1d')}</p>
        <div class="ml-12">
          <div class="inline-flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium shadow-md">
            <span class="text-lg">+</span> {lang === 'pt' ? 'Novo Fluxo' : lang === 'fr' ? 'Nouveau Flux' : lang === 'en' ? 'New Flow' : 'Nuevo Flujo'}
          </div>
          <p class="text-xs text-gray-400 mt-2">{lang === 'pt' ? '↑ Clique nesse botão no painel' : lang === 'fr' ? '↑ Cliquez sur ce bouton dans le panneau' : lang === 'en' ? '↑ Click this button in the panel' : '↑ Haga clic en este botón en el panel'}</p>
        </div>
      </div>

      <!-- Step 2: Editor visual mockup -->
      <div class="mb-12">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-black">2</div>
          <h4 class="text-lg font-bold text-gray-900">{_('step2t')}</h4>
        </div>
        <p class="text-gray-600 mb-4 ml-12">{_('step2d')}</p>
        <!-- Mockup: Editor -->
        <div class="ml-12 border-2 border-gray-200 rounded-2xl overflow-hidden shadow-lg">
          <div class="bg-white border-b px-4 py-2 flex items-center justify-between">
            <span class="text-sm font-bold text-gray-700">{lang === 'pt' ? 'Editor Visual' : lang === 'fr' ? 'Éditeur Visuel' : lang === 'en' ? 'Visual Editor' : 'Editor Visual'}</span>
            <div class="flex gap-2">
              <div class="bg-gray-100 rounded px-2 py-1 text-[10px] text-gray-500 font-mono">Ctrl+S</div>
            </div>
          </div>
          <div class="bg-gray-50 p-6 flex items-start justify-center gap-4 min-h-[280px] relative">
            <!-- Left: Toolbar -->
            <div class="bg-white rounded-xl border shadow-sm p-3 space-y-2 absolute left-4 top-4">
              <div class="w-10 h-10 rounded-lg bg-green-100 border-2 border-green-400 flex items-center justify-center text-xs font-bold text-green-700">S</div>
              <div class="w-10 h-10 rounded-lg bg-blue-100 border-2 border-blue-400 flex items-center justify-center text-xs font-bold text-blue-700">Q</div>
              <div class="w-10 h-10 rounded-lg bg-gray-100 border-2 border-gray-300 flex items-center justify-center text-xs font-bold text-gray-500">M</div>
              <div class="w-10 h-10 rounded-lg bg-purple-100 border-2 border-purple-400 flex items-center justify-center text-xs font-bold text-purple-700">F</div>
            </div>
            <!-- Center: Flow -->
            <div class="flex flex-col items-center gap-2 ml-16">
              <div class="bg-green-100 border-2 border-green-400 rounded-xl px-5 py-3 text-center shadow-sm">
                <span class="text-xs font-bold text-green-800">{lang === 'pt' ? 'Início' : lang === 'fr' ? 'Début' : lang === 'en' ? 'Start' : 'Inicio'}</span>
              </div>
              <svg class="w-5 h-8 text-gray-300"><line x1="10" y1="0" x2="10" y2="32" stroke="currentColor" stroke-width="2" /><polygon points="6,24 14,24 10,32" fill="currentColor" /></svg>
              <div class="bg-blue-100 border-2 border-blue-400 rounded-xl px-5 py-3 text-center shadow-sm">
                <span class="text-xs font-bold text-blue-800">{lang === 'pt' ? 'Qual tipo de tomada?' : lang === 'fr' ? 'Quel type de prise ?' : lang === 'en' ? 'What type of outlet?' : '¿Qué tipo de toma?'}</span>
              </div>
              <svg class="w-5 h-8 text-gray-300"><line x1="10" y1="0" x2="10" y2="32" stroke="currentColor" stroke-width="2" /><polygon points="6,24 14,24 10,32" fill="currentColor" /></svg>
              <div class="bg-blue-100 border-2 border-blue-400 rounded-xl px-5 py-3 text-center shadow-sm">
                <span class="text-xs font-bold text-blue-800">{lang === 'pt' ? 'Quantos metros de fio?' : lang === 'fr' ? 'Combien de mètres ?' : lang === 'en' ? 'How many meters of wire?' : '¿Cuántos metros de cable?'}</span>
              </div>
              <svg class="w-5 h-8 text-gray-300"><line x1="10" y1="0" x2="10" y2="32" stroke="currentColor" stroke-width="2" /><polygon points="6,24 14,24 10,32" fill="currentColor" /></svg>
              <div class="bg-purple-100 border-2 border-purple-400 rounded-xl px-5 py-3 text-center shadow-sm">
                <span class="text-xs font-bold text-purple-800">{lang === 'pt' ? 'Gerar Orçamento (IA)' : lang === 'fr' ? 'Générer Devis (IA)' : lang === 'en' ? 'Generate Quote (AI)' : 'Generar Presupuesto (IA)'}</span>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-2 border-t text-center">
            <span class="text-xs text-gray-400">{lang === 'pt' ? '↑ Assim fica o editor — arraste blocos e conecte!' : lang === 'fr' ? '↑ Voici l\'éditeur — glissez et connectez !' : lang === 'en' ? '↑ This is the editor — drag blocks and connect!' : '↑ Así se ve el editor — ¡arrastre bloques y conecte!'}</span>
          </div>
        </div>
      </div>

      <!-- Step 3: CSV -->
      <div class="mb-12">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-black">3</div>
          <h4 class="text-lg font-bold text-gray-900">{_('step3t')}</h4>
        </div>
        <p class="text-gray-600 mb-4 ml-12">{_('step3d')}</p>
        <!-- CSV Example -->
        <div class="ml-12 bg-gray-900 rounded-2xl p-5 font-mono text-sm overflow-x-auto shadow-lg">
          <div class="text-gray-400 mb-2">{lang === 'pt' ? '# Sua tabela de preços' : lang === 'fr' ? '# Votre liste de prix' : lang === 'en' ? '# Your price list' : '# Su tabla de precios'}</div>
          <div class="text-green-400">Tomada 110V: <span class="text-white">$25.00</span></div>
          <div class="text-green-400">Tomada 220V: <span class="text-white">$35.00</span></div>
          <div class="text-green-400">{lang === 'pt' ? 'Fio elétrico (por metro)' : lang === 'fr' ? 'Câble électrique (par mètre)' : lang === 'en' ? 'Electric wire (per meter)' : 'Cable eléctrico (por metro)'}: <span class="text-white">$8.50</span></div>
          <div class="text-green-400">{lang === 'pt' ? 'Disjuntor 20A' : lang === 'fr' ? 'Disjoncteur 20A' : lang === 'en' ? 'Circuit breaker 20A' : 'Disyuntor 20A'}: <span class="text-white">$45.00</span></div>
          <div class="text-green-400">{lang === 'pt' ? 'Mão de obra (por hora)' : lang === 'fr' ? 'Main d\'œuvre (par heure)' : lang === 'en' ? 'Labor (per hour)' : 'Mano de obra (por hora)'}: <span class="text-white">$80.00</span></div>
        </div>
        <p class="ml-12 text-xs text-gray-400 mt-2">{lang === 'pt' ? '↑ Exemplo de tabela de preços — cole isso no nó final' : lang === 'fr' ? '↑ Exemple de liste de prix — collez cela dans le nœud final' : lang === 'en' ? '↑ Example price list — paste this in the end node' : '↑ Ejemplo de tabla de precios — pegue esto en el nodo final'}</p>
      </div>

      <!-- Step 4: Link -->
      <div class="mb-12">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-black">4</div>
          <h4 class="text-lg font-bold text-gray-900">{_('step4t')}</h4>
        </div>
        <p class="text-gray-600 mb-4 ml-12">{_('step4d')}</p>
        <!-- Mockup: linking -->
        <div class="ml-12 bg-white border-2 border-purple-200 rounded-2xl p-5 shadow-md">
          <div class="text-xs font-bold text-gray-500 uppercase mb-3">{lang === 'pt' ? 'Opções da pergunta "Qual tipo de tomada?"' : lang === 'fr' ? 'Options de "Quel type de prise ?"' : lang === 'en' ? 'Options for "What type of outlet?"' : 'Opciones de "¿Qué tipo de toma?"'}</div>
          <div class="space-y-2.5">
            <div class="flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-3 border">
              <span class="text-sm font-medium text-gray-800 flex-1">Tomada 110V</span>
              <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>
              <span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-lg font-mono border border-green-300">Tomada 110V: $25</span>
            </div>
            <div class="flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-3 border">
              <span class="text-sm font-medium text-gray-800 flex-1">Tomada 220V</span>
              <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>
              <span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-lg font-mono border border-green-300">Tomada 220V: $35</span>
            </div>
          </div>
          <p class="text-xs text-gray-400 mt-3 text-center">{lang === 'pt' ? '↑ Cada opção vinculada ao produto do CSV (check verde = vinculado)' : lang === 'fr' ? '↑ Chaque option liée au produit du CSV (check vert = lié)' : lang === 'en' ? '↑ Each option linked to CSV product (green check = linked)' : '↑ Cada opción vinculada al producto del CSV (check verde = vinculado)'}</p>
        </div>
      </div>

      <!-- Step 5 -->
      <div class="mb-12">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-black">5</div>
          <h4 class="text-lg font-bold text-gray-900">{_('step5t')}</h4>
        </div>
        <p class="text-gray-600 ml-12">{_('step5d')}</p>
      </div>
    </section>

    <!-- ══════ TIPOS DE PERGUNTA ══════ -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-blue-600 uppercase tracking-widest mb-2">04</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-3">{_('typesTitle')}</h3>
      <p class="text-gray-600 mb-8">{_('typesIntro')}</p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Context -->
        <div class="rounded-2xl border-2 border-dashed border-gray-300 p-6 bg-gray-50">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xl">💬</span>
            <h4 class="font-bold text-gray-700">{_('ctxTitle')}</h4>
          </div>
          <p class="text-sm text-gray-600 mb-4">{_('ctxWhen')}</p>
          <div class="space-y-2 mb-4">
            <div class="bg-white rounded-lg px-3 py-2 text-sm text-gray-600 border italic">"{lang === 'pt' ? 'Quantos cômodos?' : lang === 'fr' ? 'Combien de pièces ?' : lang === 'en' ? 'How many rooms?' : '¿Cuántas habitaciones?'}"</div>
            <div class="bg-white rounded-lg px-3 py-2 text-sm text-gray-600 border italic">"{lang === 'pt' ? 'Qual o tipo do painel?' : lang === 'fr' ? 'Type de panneau ?' : lang === 'en' ? 'Panel type?' : '¿Tipo de panel?'}"</div>
            <div class="bg-white rounded-lg px-3 py-2 text-sm text-gray-600 border italic">"{lang === 'pt' ? 'Há acesso fácil?' : lang === 'fr' ? 'Accès facile ?' : lang === 'en' ? 'Easy access?' : '¿Acceso fácil?'}"</div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">{_('ctxNeedsCsv')}</span>
            <span class="bg-gray-200 text-gray-600 px-2 py-0.5 rounded text-xs font-bold">{_('ctxNo')}</span>
          </div>
        </div>

        <!-- Quote -->
        <div class="rounded-2xl border-2 border-blue-400 p-6 bg-blue-50">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xl">💰</span>
            <h4 class="font-bold text-blue-700">{_('quoteTitle')}</h4>
          </div>
          <p class="text-sm text-blue-700 mb-4">{_('quoteWhen')}</p>
          <div class="space-y-2 mb-4">
            <div class="bg-white rounded-lg px-3 py-2 text-sm text-blue-800 border border-blue-200">"{lang === 'pt' ? 'Tomada 110V ou 220V?' : lang === 'fr' ? 'Prise 110V ou 220V ?' : lang === 'en' ? '110V or 220V outlet?' : '¿Toma 110V o 220V?'}" → <span class="font-mono text-xs bg-green-100 px-1 rounded">CSV</span></div>
            <div class="bg-white rounded-lg px-3 py-2 text-sm text-blue-800 border border-blue-200">"{lang === 'pt' ? 'Quantos metros de fio?' : lang === 'fr' ? 'Mètres de câble ?' : lang === 'en' ? 'Meters of wire?' : '¿Metros de cable?'}" → <span class="font-mono text-xs bg-green-100 px-1 rounded">CSV</span></div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-blue-600">{_('ctxNeedsCsv')}</span>
            <span class="bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-bold">{_('quoteYes')}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════ REGRAS DE OURO ══════ -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-red-600 uppercase tracking-widest mb-2">⚠️</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-6">{_('rulesTitle')}</h3>

      <div class="space-y-4">
        <div class="bg-red-50 border-l-4 border-red-500 rounded-r-2xl p-5">
          <h4 class="font-bold text-red-800 mb-1">{_('rule1')}</h4>
          <p class="text-sm text-red-700">{_('rule1d')}</p>
        </div>
        <div class="bg-red-50 border-l-4 border-red-500 rounded-r-2xl p-5">
          <h4 class="font-bold text-red-800 mb-1">{_('rule2')}</h4>
          <p class="text-sm text-red-700">{_('rule2d')}</p>
        </div>
      </div>

      <div class="mt-6 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-center text-white shadow-lg">
        <p class="text-2xl font-black">{_('formula')}</p>
        <div class="flex items-center justify-center gap-3 mt-3 text-sm">
          <span class="bg-white/20 px-3 py-1 rounded-full font-semibold">📊 CSV</span>
          <span class="font-bold">+</span>
          <span class="bg-white/20 px-3 py-1 rounded-full font-semibold">🔗 {lang === 'pt' ? 'Vínculo' : lang === 'fr' ? 'Lien' : lang === 'en' ? 'Link' : 'Vínculo'}</span>
          <span class="font-bold">=</span>
          <span class="bg-white/20 px-3 py-1 rounded-full font-semibold">✨ {lang === 'pt' ? 'Perfeito' : lang === 'fr' ? 'Parfait' : lang === 'en' ? 'Perfect' : 'Perfecto'}</span>
        </div>
      </div>
    </section>

    <!-- ══════ FAQ ══════ -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-blue-600 uppercase tracking-widest mb-2">05</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-6">{_('faqTitle')}</h3>
      <div class="space-y-2">
        {#each [
          { q: 'faq1q', a: 'faq1a' },
          { q: 'faq2q', a: 'faq2a' },
          { q: 'faq3q', a: 'faq3a' }
        ] as faq, idx}
          <button onclick={() => toggleFaq(idx)} class="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-xl px-5 py-4 transition-colors cursor-pointer">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-gray-800">{_(faq.q)}</span>
              <svg class="w-5 h-5 text-gray-400 transition-transform {expandedFaq === idx ? 'rotate-180' : ''}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
            </div>
            {#if expandedFaq === idx}
              <p class="text-sm text-gray-600 mt-3 leading-relaxed">{_(faq.a)}</p>
            {/if}
          </button>
        {/each}
      </div>
    </section>

    <!-- ══════ CTA ══════ -->
    <div class="text-center pb-16">
      <button
        onclick={() => goto('/admin/flows')}
        class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-4 rounded-2xl text-lg font-bold hover:shadow-xl cursor-pointer transition-all shadow-lg active:scale-95"
      >
        {_('cta')} →
      </button>
    </div>
  </main>
</div>
