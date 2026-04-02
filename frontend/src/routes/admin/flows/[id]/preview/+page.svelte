<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { FlowsService } from '$lib/services/flows.service';
  import type { Flow, FlowNode, FlowEdge } from '$lib/dto/flows/types';

  const service = new FlowsService();

  let flow = $state<Flow | null>(null);
  let loading = $state(true);
  let error = $state('');

  // Executor state
  let phase = $state<'form' | 'questions' | 'end'>('form');
  let clientData = $state({ name: '', email: '', phone: '', address: '' });
  let currentNodeId = $state<string | null>(null);
  let answers = $state<{ node_id: string; question: string; value: string }[]>([]);
  let endNode = $state<FlowNode | null>(null);
  let resultText = $state('');
  let inputValue = $state('');

  let currentNode = $derived(flow?.nodes.find(n => n.id === currentNodeId) || null);
  let totalQuestions = $derived(flow?.nodes.filter(n => n.type === 'question').length || 0);
  let answeredCount = $derived(answers.length);
  let progressPercent = $derived(totalQuestions > 0 ? Math.round((answeredCount / totalQuestions) * 100) : 0);

  onMount(async () => {
    try {
      flow = await service.getById(page.params.id);
      if (!flow) error = 'Fluxo não encontrado';
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  function startQuestions() {
    if (!clientData.name.trim() || !clientData.email.trim()) return;
    phase = 'questions';
    const startNode = flow!.nodes.find(n => n.type === 'start');
    if (!startNode) return;
    const edge = flow!.edges.find(e => e.source === startNode.id);
    if (edge) {
      currentNodeId = edge.target;
      processCurrentNode();
    }
  }

  function processCurrentNode() {
    if (!currentNode) return;
    if (currentNode.type === 'message') {
      setTimeout(() => {
        const edge = flow!.edges.find(e => e.source === currentNodeId);
        if (edge) {
          currentNodeId = edge.target;
          processCurrentNode();
        }
      }, 2500);
    } else if (currentNode.type === 'end') {
      endNode = currentNode;
      phase = 'end';
    }
  }

  function selectAnswer(value: string, handleId?: string) {
    if (!currentNode) return;
    answers = [...answers, {
      node_id: currentNode.id,
      question: currentNode.data.title,
      value
    }];
    let nextEdge: FlowEdge | undefined;
    if (handleId) {
      nextEdge = flow!.edges.find(e => e.source === currentNodeId && e.sourceHandle === handleId);
    }
    if (!nextEdge) {
      nextEdge = flow!.edges.find(e => e.source === currentNodeId && !e.sourceHandle);
    }
    if (!nextEdge) {
      nextEdge = flow!.edges.find(e => e.source === currentNodeId);
    }
    if (nextEdge) {
      currentNodeId = nextEdge.target;
      processCurrentNode();
    }
  }

  function goBack() {
    if (answers.length === 0) {
      phase = 'form';
      return;
    }
    const last = answers[answers.length - 1];
    answers = answers.slice(0, -1);
    currentNodeId = last.node_id;
    phase = 'questions';
    endNode = null;
  }

  function resetSimulation() {
    phase = 'form';
    clientData = { name: '', email: '', phone: '', address: '' };
    currentNodeId = null;
    answers = [];
    endNode = null;
    resultText = '';
    inputValue = '';
  }

</script>

<div class="min-h-screen bg-gray-100 flex flex-col">
  <!-- Header admin do preview -->
  <header class="bg-white border-b px-6 py-3 flex items-center justify-between z-10">
    <div class="flex items-center gap-3">
      <button onclick={() => goto('/admin/scheduling')} class="text-gray-400 hover:text-gray-700 cursor-pointer transition-colors p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
        </svg>
      </button>
      <div class="h-5 w-px bg-gray-200"></div>
      <div>
        <h1 class="text-sm font-bold text-gray-900">Previa: {flow?.name || '...'}</h1>
        <p class="text-xs text-gray-500">Simulação do formulário — como o lead vai ver</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <button
        onclick={resetSimulation}
        class="text-xs font-medium text-gray-600 hover:text-orange-600 bg-gray-100 hover:bg-orange-50 rounded-md px-3 py-1.5 cursor-pointer transition-colors flex items-center gap-1"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
        </svg>
        Reiniciar
      </button>
      <button
        onclick={() => goto(`/admin/flows/${page.params.id}/edit`)}
        class="text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-md px-3 py-1.5 cursor-pointer transition-colors flex items-center gap-1"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z" />
        </svg>
        Editar formulário
      </button>
      {#if flow?.slug}
        <a
          href="/q/{flow.slug}"
          target="_blank"
          class="text-xs font-medium text-green-600 hover:text-green-700 bg-green-50 hover:bg-green-100 rounded-md px-3 py-1.5 cursor-pointer transition-colors flex items-center gap-1"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
          </svg>
          Link público
        </a>
      {/if}
    </div>
  </header>

  <!-- Info lateral com dados de debug -->
  <div class="flex-1 flex">
    <!-- Questionário simulado (centralizado) -->
    <div class="flex-1 flex items-center justify-center p-6">
      <div class="bg-white rounded-2xl shadow-lg border border-gray-200 max-w-md w-full overflow-hidden">

        {#if loading}
          <div class="p-16 text-center">
            <div class="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p class="text-sm text-gray-500">Carregando...</p>
          </div>

        {:else if error}
          <div class="p-12 text-center text-red-600 text-sm">{error}</div>

        {:else if phase === 'form'}
          <div class="p-8">
            <h2 class="text-xl font-bold text-gray-900 mb-1">{flow?.name}</h2>
            <p class="text-sm text-gray-500 mb-6">Obtenez votre devis en quelques minutes</p>
            <div class="space-y-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide">Nom *</label>
                <input type="text" bind:value={clientData.name} class="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide">E-mail *</label>
                <input type="email" bind:value={clientData.email} class="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide">Téléphone</label>
                <input type="tel" bind:value={clientData.phone} class="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide">Adresse</label>
                <input type="text" bind:value={clientData.address} class="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow" />
              </div>
              <button
                onclick={startQuestions}
                disabled={!clientData.name.trim() || !clientData.email.trim()}
                class="w-full bg-blue-600 text-white py-3 rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors mt-2"
              >
                Commencer
              </button>
            </div>
          </div>

        {:else if phase === 'questions' && currentNode}
          <div class="bg-gray-50 px-6 py-3 flex items-center justify-between border-b border-gray-100">
            <span class="text-xs font-medium text-gray-500">Question {answeredCount + 1} / {totalQuestions}</span>
            <div class="flex items-center gap-2">
              <div class="w-24 bg-gray-200 rounded-full h-1.5">
                <div class="bg-blue-600 h-1.5 rounded-full transition-all duration-300" style="width: {progressPercent}%"></div>
              </div>
              <span class="text-xs text-gray-400">{progressPercent}%</span>
            </div>
          </div>
          <div class="p-8">
            {#if currentNode.type === 'message'}
              <div class="text-center py-4">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">{currentNode.data.title}</h3>
                <p class="text-sm text-gray-600">{currentNode.data.message}</p>
              </div>
            {:else}
              <h3 class="text-lg font-semibold text-gray-900 mb-1">{currentNode.data.title}</h3>
              {#if currentNode.data.tooltip}
                <p class="text-xs text-gray-400 mb-4">{currentNode.data.tooltip}</p>
              {:else}
                <div class="mb-4"></div>
              {/if}

              {#if currentNode.data.questionType === 'single_choice' && currentNode.data.options}
                <div class="grid grid-cols-2 gap-2">
                  {#each currentNode.data.options as opt}
                    <button
                      onclick={() => selectAnswer(opt.value, opt.id)}
                      class="border-2 border-gray-200 rounded-xl px-3 py-3.5 text-center text-sm font-medium hover:border-blue-500 hover:bg-blue-50 transition-all cursor-pointer"
                    >
                      {opt.label}
                    </button>
                  {/each}
                </div>
              {:else if currentNode.data.questionType === 'yes_no'}
                <div class="grid grid-cols-2 gap-3">
                  <button onclick={() => selectAnswer('Oui', 'yes')} class="border-2 border-gray-200 rounded-xl px-4 py-4 text-center font-medium hover:border-green-500 hover:bg-green-50 transition-all cursor-pointer">Oui</button>
                  <button onclick={() => selectAnswer('Non', 'no')} class="border-2 border-gray-200 rounded-xl px-4 py-4 text-center font-medium hover:border-red-400 hover:bg-red-50 transition-all cursor-pointer">Non</button>
                </div>
              {:else if currentNode.data.questionType === 'number'}
                <div class="flex gap-2">
                  <input type="number" bind:value={inputValue} class="flex-1 border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" placeholder="Entrez un nombre" />
                  <button onclick={() => { selectAnswer(inputValue); inputValue = ''; }} disabled={!inputValue} class="bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-40 cursor-pointer transition-colors">Suivant</button>
                </div>
              {:else}
                <div class="flex gap-2">
                  <input type="text" bind:value={inputValue} class="flex-1 border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" placeholder="Votre réponse" />
                  <button onclick={() => { selectAnswer(inputValue); inputValue = ''; }} disabled={!inputValue.trim()} class="bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-40 cursor-pointer transition-colors">Suivant</button>
                </div>
              {/if}
            {/if}
            <button onclick={goBack} class="mt-6 text-xs text-gray-400 hover:text-gray-600 cursor-pointer transition-colors flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
              </svg>
              Retour
            </button>
          </div>

        {:else if phase === 'end' && endNode}
          <div class="p-8">
            {#if endNode.data.endType === 'scheduling'}
              <div class="text-center">
                <div class="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-3">
                  <svg class="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                  </svg>
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">{endNode.data.title}</h3>
                <p class="text-sm text-gray-600 mb-2">{endNode.data.message || 'Aqui o lead verá o calendário para agendar.'}</p>
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-700">
                  (Preview) O calendário de agendamento aparecerá aqui no formulário real.
                </div>
              </div>
            {:else}
              <div class="text-center">
                <div class="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
                  <svg class="w-7 h-7 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
                  </svg>
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">{endNode.data.title}</h3>
                <p class="text-sm text-gray-600">{endNode.data.message || 'Obrigado pelas suas respostas!'}</p>
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>

    <!-- Painel lateral: respostas coletadas em tempo real -->
    <aside class="w-80 bg-white border-l overflow-y-auto p-4 hidden lg:block">
      <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Dados coletados</h3>

      {#if clientData.name || clientData.email}
        <div class="mb-4">
          <p class="text-xs font-medium text-gray-700 mb-1">Cliente</p>
          <div class="bg-gray-50 rounded-md p-2.5 text-xs text-gray-600 space-y-0.5">
            {#if clientData.name}<p><span class="font-medium">Nome:</span> {clientData.name}</p>{/if}
            {#if clientData.email}<p><span class="font-medium">Email:</span> {clientData.email}</p>{/if}
            {#if clientData.phone}<p><span class="font-medium">Tel:</span> {clientData.phone}</p>{/if}
            {#if clientData.address}<p><span class="font-medium">End:</span> {clientData.address}</p>{/if}
          </div>
        </div>
      {/if}

      {#if answers.length > 0}
        <p class="text-xs font-medium text-gray-700 mb-1">Respostas ({answers.length})</p>
        <div class="space-y-1.5">
          {#each answers as answer, i}
            <div class="bg-gray-50 rounded-md p-2.5 text-xs">
              <p class="text-gray-500">{i + 1}. {answer.question}</p>
              <p class="font-medium text-gray-800">{answer.value}</p>
            </div>
          {/each}
        </div>
      {:else}
        <p class="text-xs text-gray-400 italic">Nenhuma resposta ainda. Inicie a simulação.</p>
      {/if}

      {#if flow}
        <div class="mt-6 pt-4 border-t">
          <p class="text-xs font-medium text-gray-700 mb-1">Info do fluxo</p>
          <div class="bg-gray-50 rounded-md p-2.5 text-xs text-gray-600 space-y-0.5">
            <p><span class="font-medium">Nós:</span> {flow.nodes.length}</p>
            <p><span class="font-medium">Conexões:</span> {flow.edges.length}</p>
            <p><span class="font-medium">Status:</span> {flow.status}</p>
            <p><span class="font-medium">Versão:</span> {flow.version}</p>
          </div>
        </div>
      {/if}
    </aside>
  </div>
</div>
