<script lang="ts">
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { FlowsService } from '$lib/services/flows.service';
  import { SubmissionsService } from '$lib/services/submissions.service';
  import type { Flow, FlowNode, FlowEdge } from '$lib/dto/flows/types';

  const flowService = new FlowsService();
  const submissionService = new SubmissionsService();

  let flow = $state<Flow | null>(null);
  let loading = $state(true);
  let error = $state('');

  // Executor state
  let phase = $state<'form' | 'questions' | 'end' | 'scheduling'>('form');
  let clientData = $state({ name: '', email: '', phone: '', address: '' });
  let currentNodeId = $state<string | null>(null);
  let answers = $state<{ node_id: string; question: string; value: string; label?: string }[]>([]);
  let endNode = $state<FlowNode | null>(null);
  let submitting = $state(false);
  let inputValue = $state('');

  // Scheduling state
  let schedulingStep = $state<'calendar' | 'time' | 'confirm' | 'done'>('calendar');
  let availableDates = $state<{ date: string; available: boolean; slots_count: number }[]>([]);
  let availableSlots = $state<string[]>([]);
  let selectedDate = $state('');
  let selectedTime = $state('');
  let calMonth = $state(new Date().getMonth());
  let calYear = $state(new Date().getFullYear());
  let loadingDates = $state(false);
  let loadingSlots = $state(false);
  let schedulingResult = $state<{ message: string } | null>(null);

  // Quote result
  let quoteData = $state<{
    items: { description: string; unit_price: number; quantity: number; subtotal: number }[];
    subtotal: number;
    taxes_tps: number;
    taxes_tvq: number;
    total: number;
    recommendations: string;
    notes: string;
  } | null>(null);
  let resultText = $state('');
  let resultType = $state<'quote' | 'fallback' | 'error' | ''>('');

  let currentNode = $derived(flow?.nodes.find(n => n.id === currentNodeId) || null);
  let totalQuestions = $derived(flow?.nodes.filter(n => n.type === 'question').length || 0);
  let answeredCount = $derived(answers.length);
  let progressPercent = $derived(totalQuestions > 0 ? Math.round((answeredCount / totalQuestions) * 100) : 0);

  onMount(async () => {
    try {
      const slug = page.params.slug;
      if (slug) {
        flow = await flowService.getBySlug(slug);
      }
      if (!flow) error = 'Questionnaire non trouve';
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
      if (currentNode.data.endType === 'scheduling') {
        phase = 'scheduling';
        schedulingStep = 'calendar';
        loadAvailableDates(calMonth + 1, calYear);
      } else if (currentNode.data.endType === 'message') {
        phase = 'end';
        resultType = 'message';
      } else {
        phase = 'end';
        submitToBackend();
      }
    }
  }

  async function submitToBackend() {
    if (!flow || !endNode) return;
    submitting = true;
    resultText = '';
    quoteData = null;
    resultType = '';

    try {
      const payload = {
        flow_id: flow._id || '',
        flow_slug: flow.slug,
        client_name: clientData.name,
        client_email: clientData.email,
        client_phone: clientData.phone || undefined,
        client_address: clientData.address || undefined,
        answers,
        end_node_id: endNode.id
      };

      if (endNode.data.endType === 'quote') {
        const res = await fetch('/api/generate-quote', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const result = await res.json();
          quoteData = result.quote_data || null;
          resultText = result.quote_text || '';
          resultType = quoteData ? 'quote' : 'fallback';
        } else {
          const result = await submissionService.submit(payload);
          resultText = result.quote_text || 'Votre demande a ete enregistree. Un specialiste vous contactera.';
          resultType = 'fallback';
        }
      } else {
        const result = await submissionService.submit(payload);
        resultText = result.quote_text || 'Votre demande a ete enregistree. Merci!';
        resultType = 'fallback';
      }
    } catch (e: any) {
      resultText = 'Erreur lors de l\'envoi. Veuillez reessayer.';
      resultType = 'error';
    } finally {
      submitting = false;
    }
  }

  function selectAnswer(value: string | number, handleId?: string, label?: string) {
    if (!currentNode) return;
    answers = [...answers, {
      node_id: currentNode.id,
      question: currentNode.data.title,
      value: String(value),
      label: label || String(value)
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

  // ── Scheduling functions ──────────────────────────────
  async function loadAvailableDates(month: number, year: number) {
    loadingDates = true;
    try {
      const res = await fetch(`/api/scheduling?action=dates&month=${month}&year=${year}`);
      if (res.ok) availableDates = await res.json();
    } catch (e) { /* silent */ }
    loadingDates = false;
  }

  async function selectDate(date: string) {
    selectedDate = date;
    selectedTime = '';
    loadingSlots = true;
    try {
      const res = await fetch(`/api/scheduling?action=slots&date=${date}`);
      if (res.ok) availableSlots = await res.json();
    } catch (e) { /* silent */ }
    loadingSlots = false;
    schedulingStep = 'time';
  }

  function selectTime(time: string) {
    selectedTime = time;
  }

  function confirmScheduling() {
    schedulingStep = 'confirm';
  }

  async function submitScheduling() {
    submitting = true;
    try {
      const res = await fetch('/api/scheduling', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          flow_id: flow?._id || '',
          flow_slug: flow?.slug || '',
          lead_name: clientData.name,
          lead_email: clientData.email,
          lead_phone: clientData.phone,
          lead_address: clientData.address,
          qualifying_answers: answers,
          scheduled_date: selectedDate,
          scheduled_time: selectedTime
        })
      });
      if (res.ok) {
        const data = await res.json();
        schedulingResult = data;
        schedulingStep = 'done';
      }
    } catch (e) { /* silent */ }
    submitting = false;
  }

  function prevCalMonth() {
    if (calMonth === 0) { calMonth = 11; calYear--; }
    else calMonth--;
    loadAvailableDates(calMonth + 1, calYear);
  }

  function nextCalMonth() {
    if (calMonth === 11) { calMonth = 0; calYear++; }
    else calMonth++;
    loadAvailableDates(calMonth + 1, calYear);
  }

  function formatDateBR(dateStr: string): string {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' });
  }

  const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];
  const monthNames = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

  let calDaysInMonth = $derived(new Date(calYear, calMonth + 1, 0).getDate());
  let calFirstDay = $derived(new Date(calYear, calMonth, 1).getDay());
  let dateMap = $derived.by(() => {
    const map: Record<string, { available: boolean; slots_count: number }> = {};
    for (const d of availableDates) map[d.date] = d;
    return map;
  });
  let canGoPrev = $derived.by(() => {
    const now = new Date();
    return calYear > now.getFullYear() || (calYear === now.getFullYear() && calMonth > now.getMonth());
  });
  let morningSlots = $derived(availableSlots.filter(s => parseInt(s.split(':')[0]) < 12));
  let afternoonSlots = $derived(availableSlots.filter(s => parseInt(s.split(':')[0]) >= 12));

  function formatCurrency(val: number): string {
    return val.toLocaleString('fr-CA', { style: 'currency', currency: 'CAD' });
  }

  function printQuote() {
    window.print();
  }
</script>

<svelte:head>
  <style>
    @media print {
      body * { visibility: hidden; }
      .quote-card, .quote-card * { visibility: visible; }
      .quote-card { position: absolute; left: 0; top: 0; width: 100%; }
      .no-print { display: none !important; }
    }
  </style>
</svelte:head>

<div class="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex items-center justify-center p-4" style="font-weight: 400;">
  <div class="bg-white rounded-2xl shadow-lg border border-gray-200 max-w-lg w-full overflow-hidden text-base">

    {#if loading}
      <div class="p-16 text-center">
        <div class="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p class="text-sm text-gray-500">Carregando...</p>
      </div>

    {:else if error}
      <div class="p-12 text-center text-red-600 text-sm">{error}</div>

    {:else if phase === 'form'}
      <div class="p-8">
        <h2 class="text-2xl font-semibold text-gray-900 mb-2">{flow?.name}</h2>
        <p class="text-base text-gray-500 mb-8">Preencha seus dados para agendar</p>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1.5">Nome completo *</label>
            <input type="text" bind:value={clientData.name} class="w-full border border-gray-200 rounded-xl px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1.5">E-mail *</label>
            <input type="email" bind:value={clientData.email} class="w-full border border-gray-200 rounded-xl px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1.5">WhatsApp</label>
            <input type="tel" bind:value={clientData.phone} class="w-full border border-gray-200 rounded-xl px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1.5">Endereco</label>
            <input type="text" bind:value={clientData.address} class="w-full border border-gray-200 rounded-xl px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow" />
          </div>
          <button
            onclick={startQuestions}
            disabled={!clientData.name.trim() || !clientData.email.trim()}
            class="w-full bg-blue-600 text-white py-3.5 rounded-xl text-base font-semibold hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors mt-3"
          >
            Comecar
          </button>
        </div>
      </div>

    {:else if phase === 'questions' && currentNode}
      <!-- Progress -->
      <div class="bg-gray-50 px-6 py-3.5 flex items-center justify-between border-b border-gray-100">
        <span class="text-sm font-medium text-gray-500">Pergunta {answeredCount + 1} / {totalQuestions}</span>
        <div class="flex items-center gap-2">
          <div class="w-28 bg-gray-200 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: {progressPercent}%"></div>
          </div>
          <span class="text-sm text-gray-400">{progressPercent}%</span>
        </div>
      </div>

      <div class="p-8">
        {#if currentNode.type === 'message'}
          <div class="text-center py-6">
            <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{currentNode.data.title}</h3>
            <p class="text-base text-gray-600">{currentNode.data.message}</p>
          </div>
        {:else}
          <h3 class="text-xl font-semibold text-gray-900 mb-2">{currentNode.data.title}</h3>

          {#if currentNode.data.tooltip}
            <p class="text-sm text-gray-400 mb-5">{currentNode.data.tooltip}</p>
          {:else}
            <div class="mb-5"></div>
          {/if}

          {#if currentNode.data.questionType === 'single_choice' && currentNode.data.options}
            <div class="grid grid-cols-2 gap-3">
              {#each currentNode.data.options as opt}
                <button
                  onclick={() => selectAnswer(opt.value, opt.id, opt.label)}
                  class="border-2 border-gray-200 rounded-xl px-4 py-4 text-center text-base font-medium hover:border-blue-500 hover:bg-blue-50 transition-all cursor-pointer"
                >
                  {opt.label}
                </button>
              {/each}
            </div>
          {:else if currentNode.data.questionType === 'yes_no'}
            <div class="grid grid-cols-2 gap-3">
              <button
                onclick={() => selectAnswer('Oui', 'yes')}
                class="border-2 border-gray-200 rounded-xl px-4 py-5 text-center text-lg font-medium hover:border-green-500 hover:bg-green-50 transition-all cursor-pointer"
              >
                Sim
              </button>
              <button
                onclick={() => selectAnswer('Non', 'no')}
                class="border-2 border-gray-200 rounded-xl px-4 py-5 text-center text-lg font-medium hover:border-red-400 hover:bg-red-50 transition-all cursor-pointer"
              >
                Nao
              </button>
            </div>
          {:else if currentNode.data.questionType === 'number'}
            <div class="flex gap-2">
              <input
                type="number"
                bind:value={inputValue}
                class="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                placeholder="Digite um numero"
              />
              <button
                onclick={() => { selectAnswer(inputValue); inputValue = ''; }}
                disabled={!inputValue}
                class="bg-blue-600 text-white px-6 py-3 rounded-xl text-base font-medium hover:bg-blue-700 disabled:opacity-40 cursor-pointer transition-colors"
              >
                Proximo
              </button>
            </div>
          {:else}
            <div class="flex gap-2">
              <input
                type="text"
                bind:value={inputValue}
                class="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                placeholder="Sua resposta"
              />
              <button
                onclick={() => { selectAnswer(inputValue); inputValue = ''; }}
                disabled={!inputValue.trim()}
                class="bg-blue-600 text-white px-6 py-3 rounded-xl text-base font-medium hover:bg-blue-700 disabled:opacity-40 cursor-pointer transition-colors"
              >
                Proximo
              </button>
            </div>
          {/if}
        {/if}

        <button
          onclick={goBack}
          class="mt-6 text-sm text-gray-400 hover:text-gray-600 cursor-pointer transition-colors flex items-center gap-1.5"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          Voltar
        </button>
      </div>

    {:else if phase === 'end' && endNode}

      {#if submitting}
        <div class="p-8">
          <div class="text-center py-8">
            <div class="w-12 h-12 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-5"></div>
            <p class="text-base text-gray-800 font-semibold">Processando suas respostas...</p>
            <p class="text-sm text-gray-400 mt-2">Aguarde um momento</p>
          </div>
        </div>

      {:else if endNode.data.endType === 'specialist'}
        <div class="p-8 text-center">
          <div class="w-14 h-14 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
            <svg class="w-7 h-7 text-red-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">{endNode.data.title}</h3>
          <p class="text-base text-gray-600 mb-5">{endNode.data.message}</p>
          <div class="bg-green-50 border border-green-200 rounded-xl p-4 text-sm text-green-700">
            Seus dados foram registrados. Entraremos em contato em ate 24h.
          </div>
        </div>

      {:else if endNode.data.endType === 'quote' && quoteData}
        <!-- DEVIS PROFESSIONNEL -->
        <div class="quote-card">
          <!-- Header -->
          <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-5">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-bold">Resumo</h3>
                <p class="text-blue-200 text-xs mt-0.5">IT Valley</p>
              </div>
              <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div class="mt-3 text-sm">
              <p class="font-medium">{clientData.name}</p>
              {#if clientData.address}
                <p class="text-blue-200 text-xs">{clientData.address}</p>
              {/if}
            </div>
          </div>

          <!-- Items -->
          <div class="px-6 py-4">
            <table class="w-full text-sm" data-testid="quote-items-table">
              <thead>
                <tr class="text-xs text-gray-400 uppercase tracking-wider border-b border-gray-100">
                  <th class="text-left py-2 font-medium">Produit / Service</th>
                  <th class="text-center py-2 font-medium w-12">Qte</th>
                  <th class="text-right py-2 font-medium">Prix</th>
                </tr>
              </thead>
              <tbody>
                {#each quoteData.items as item}
                  <tr class="border-b border-gray-50">
                    <td class="py-2.5 text-gray-800 font-medium">{item.description}</td>
                    <td class="py-2.5 text-center text-gray-500">{item.quantity}</td>
                    <td class="py-2.5 text-right font-medium tabular-nums {item.subtotal === 0 ? 'text-amber-600 italic' : 'text-gray-800'}">{item.subtotal === 0 ? 'A consulter' : formatCurrency(item.subtotal)}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>

          <!-- Totals -->
          <div class="px-6 pb-4">
            <div class="bg-gray-50 rounded-xl p-4 space-y-1.5">
              <div class="flex justify-between text-sm text-gray-600">
                <span>Sous-total</span>
                <span class="tabular-nums">{formatCurrency(quoteData.subtotal)}</span>
              </div>
              <div class="flex justify-between text-sm text-gray-500">
                <span>TPS (5%)</span>
                <span class="tabular-nums">{formatCurrency(quoteData.taxes_tps)}</span>
              </div>
              <div class="flex justify-between text-sm text-gray-500">
                <span>TVQ (9,975%)</span>
                <span class="tabular-nums">{formatCurrency(quoteData.taxes_tvq)}</span>
              </div>
              <div class="border-t border-gray-200 pt-2 mt-2 flex justify-between text-base font-bold text-gray-900">
                <span>Total</span>
                <span class="tabular-nums text-blue-700">{formatCurrency(quoteData.total)}</span>
              </div>
            </div>
          </div>

          <!-- Recommendations -->
          {#if quoteData.recommendations}
            <div class="px-6 pb-3">
              <div class="bg-blue-50 border border-blue-100 rounded-lg p-3">
                <p class="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-1">Recommandations</p>
                <p class="text-xs text-blue-800 leading-relaxed">{quoteData.recommendations}</p>
              </div>
            </div>
          {/if}

          <!-- Notes -->
          {#if quoteData.notes}
            <div class="px-6 pb-3">
              <div class="bg-amber-50 border border-amber-100 rounded-lg p-3">
                <p class="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1">Notes</p>
                <p class="text-xs text-amber-800 leading-relaxed">{quoteData.notes}</p>
              </div>
            </div>
          {/if}

          <!-- Footer -->
          <div class="px-6 pb-4">
            <div class="grid grid-cols-2 gap-2 text-xs text-gray-400">
              <span>Validite: 30 jours</span>
              <span class="text-right">Inspection gratuite</span>
              <span>Garantie 2 ans</span>
              <span class="text-right">Permis inclus</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="px-6 pb-6 flex gap-2 no-print">
            <button
              onclick={printQuote}
              class="flex-1 bg-blue-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-700 cursor-pointer transition-colors flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.72 13.829c-.24.03-.48.062-.72.096m.72-.096a42.415 42.415 0 0110.56 0m-10.56 0L6.34 18m10.94-4.171c.24.03.48.062.72.096m-.72-.096L17.66 18m0 0l.229 2.523a1.125 1.125 0 01-1.12 1.227H7.231c-.662 0-1.18-.568-1.12-1.227L6.34 18m11.318 0h1.091A2.25 2.25 0 0021 15.75V9.456c0-1.081-.768-2.015-1.837-2.175a48.055 48.055 0 00-1.913-.247M6.34 18H5.25A2.25 2.25 0 013 15.75V9.456c0-1.081.768-2.015 1.837-2.175a48.041 48.041 0 011.913-.247m10.5 0a48.536 48.536 0 00-10.5 0m10.5 0V3.375c0-.621-.504-1.125-1.125-1.125h-8.25c-.621 0-1.125.504-1.125 1.125v3.659M18 10.5h.008v.008H18V10.5zm-3 0h.008v.008H15V10.5z" />
              </svg>
              Imprimer / PDF
            </button>
          </div>
        </div>

      {:else if endNode.data.endType === 'quote' && resultText}
        <!-- Fallback: texto simples se quote_data nao veio -->
        <div class="p-8">
          <div class="text-center mb-4">
            <div class="w-14 h-14 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-3">
              <svg class="w-7 h-7 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900">Sua solicitacao foi registrada!</h3>
          </div>
          <pre class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs whitespace-pre-wrap font-mono text-gray-700 max-h-80 overflow-y-auto">{resultText}</pre>
        </div>

      {:else if resultType === 'message'}
        <div class="p-8 text-center">
          <div class="w-14 h-14 rounded-full bg-amber-100 flex items-center justify-center mx-auto mb-3">
            <svg class="w-7 h-7 text-amber-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">{endNode.data.title}</h3>
          <p class="text-sm text-gray-600">{endNode.data.message}</p>
        </div>

      {:else}
        <div class="p-8 text-center">
          <div class="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
            <svg class="w-7 h-7 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">{endNode.data.title}</h3>
          <p class="text-sm text-gray-600">Obrigado pelas suas respostas!</p>
          {#if resultText}
            <p class="text-sm text-gray-500 mt-3">{resultText}</p>
          {/if}
        </div>
      {/if}

    <!-- ==================== SCHEDULING ==================== -->
    {:else if phase === 'scheduling'}

      {#if schedulingStep === 'calendar'}
        <div class="p-6">
          <div class="text-center mb-5">
            <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-3">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900">Escolha o dia</h3>
            <p class="text-sm text-gray-500">{endNode?.data.message || 'Selecione uma data disponivel'}</p>
          </div>

          <!-- Calendar -->
          <div class="border border-gray-200 rounded-xl overflow-hidden">
            <!-- Month nav -->
            <div class="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
              <button onclick={prevCalMonth} disabled={!canGoPrev} class="p-1.5 rounded-lg hover:bg-gray-200 disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer transition-colors">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
              </button>
              <span class="text-sm font-semibold text-gray-800">{monthNames[calMonth]} {calYear}</span>
              <button onclick={nextCalMonth} class="p-1.5 rounded-lg hover:bg-gray-200 cursor-pointer transition-colors">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
              </button>
            </div>

            <!-- Weekday headers -->
            <div class="grid grid-cols-7 border-b border-gray-100">
              {#each weekdays as wd}
                <div class="py-2 text-center text-[10px] font-semibold text-gray-400 uppercase">{wd}</div>
              {/each}
            </div>

            <!-- Days -->
            {#if loadingDates}
              <div class="py-12 text-center">
                <div class="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
            {:else}
              <div class="grid grid-cols-7 gap-px p-2">
                {#each Array(calFirstDay) as _}<div></div>{/each}
                {#each Array(calDaysInMonth) as _, i}
                  {@const day = i + 1}
                  {@const dateStr = `${calYear}-${String(calMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`}
                  {@const info = dateMap[dateStr]}
                  {@const avail = info?.available ?? false}
                  {@const isToday = new Date().toISOString().slice(0, 10) === dateStr}
                  <button
                    onclick={() => avail && selectDate(dateStr)}
                    disabled={!avail}
                    class="relative aspect-square flex items-center justify-center rounded-lg text-sm font-medium transition-all
                    {selectedDate === dateStr
                      ? 'bg-blue-600 text-white shadow-md scale-110'
                      : avail
                        ? 'text-gray-800 hover:bg-blue-50 hover:text-blue-600 cursor-pointer'
                        : 'text-gray-300 cursor-not-allowed'}"
                  >
                    {day}
                    {#if isToday && selectedDate !== dateStr}
                      <span class="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-blue-500"></span>
                    {/if}
                  </button>
                {/each}
              </div>
            {/if}
          </div>

          <button onclick={goBack} class="mt-4 text-xs text-gray-400 hover:text-gray-600 cursor-pointer transition-colors flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
            Voltar
          </button>
        </div>

      {:else if schedulingStep === 'time'}
        <div class="p-6">
          <div class="text-center mb-5">
            <h3 class="text-lg font-bold text-gray-900">Escolha o horario</h3>
            <p class="text-sm text-gray-500 capitalize">{formatDateBR(selectedDate)}</p>
          </div>

          {#if loadingSlots}
            <div class="py-12 text-center">
              <div class="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          {:else}
            <!-- Morning -->
            {#if morningSlots.length > 0}
              <div class="mb-4">
                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Manha</p>
                <div class="grid grid-cols-3 gap-2">
                  {#each morningSlots as slot}
                    <button
                      onclick={() => selectTime(slot)}
                      class="py-2.5 rounded-xl border-2 text-sm font-semibold transition-all cursor-pointer
                      {selectedTime === slot ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50'}"
                    >{slot}</button>
                  {/each}
                </div>
              </div>
            {/if}
            <!-- Afternoon -->
            {#if afternoonSlots.length > 0}
              <div class="mb-4">
                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Tarde</p>
                <div class="grid grid-cols-3 gap-2">
                  {#each afternoonSlots as slot}
                    <button
                      onclick={() => selectTime(slot)}
                      class="py-2.5 rounded-xl border-2 text-sm font-semibold transition-all cursor-pointer
                      {selectedTime === slot ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50'}"
                    >{slot}</button>
                  {/each}
                </div>
              </div>
            {/if}
            {#if availableSlots.length === 0}
              <p class="text-center text-gray-400 py-8">Nenhum horario disponivel nesta data</p>
            {/if}
          {/if}

          {#if selectedTime}
            <button
              onclick={confirmScheduling}
              class="w-full bg-blue-600 text-white py-3 rounded-lg text-sm font-semibold hover:bg-blue-700 cursor-pointer transition-colors mt-2"
            >
              Continuar
            </button>
          {/if}

          <button onclick={() => { schedulingStep = 'calendar'; selectedTime = ''; }} class="mt-3 text-xs text-gray-400 hover:text-gray-600 cursor-pointer transition-colors flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
            Voltar ao calendario
          </button>
        </div>

      {:else if schedulingStep === 'confirm'}
        <div class="p-6">
          <div class="text-center mb-5">
            <h3 class="text-lg font-bold text-gray-900">Confirme seu agendamento</h3>
            <p class="text-sm text-gray-500">Verifique os dados antes de confirmar</p>
          </div>

          <div class="bg-gray-50 rounded-xl p-5 space-y-3 mb-5">
            <div class="flex justify-between"><span class="text-xs text-gray-500">Nome</span><span class="text-sm font-medium text-gray-900">{clientData.name}</span></div>
            <div class="flex justify-between"><span class="text-xs text-gray-500">E-mail</span><span class="text-sm font-medium text-gray-900">{clientData.email}</span></div>
            {#if clientData.phone}
              <div class="flex justify-between"><span class="text-xs text-gray-500">Telefone</span><span class="text-sm font-medium text-gray-900">{clientData.phone}</span></div>
            {/if}
            <hr class="border-gray-200" />
            <div class="flex justify-between"><span class="text-xs text-gray-500">Data</span><span class="text-sm font-medium text-gray-900 capitalize">{formatDateBR(selectedDate)}</span></div>
            <div class="flex justify-between"><span class="text-xs text-gray-500">Horario</span><span class="text-sm font-medium text-gray-900">{selectedTime}</span></div>
          </div>

          <button
            onclick={submitScheduling}
            disabled={submitting}
            class="w-full bg-blue-600 text-white py-3 rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 cursor-pointer transition-colors"
          >
            {#if submitting}
              <span class="inline-flex items-center gap-2">
                <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Agendando...
              </span>
            {:else}
              Confirmar Agendamento
            {/if}
          </button>

          <button onclick={() => schedulingStep = 'time'} class="mt-3 text-xs text-gray-400 hover:text-gray-600 cursor-pointer transition-colors flex items-center gap-1 mx-auto">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
            Voltar
          </button>
        </div>

      {:else if schedulingStep === 'done'}
        <div class="p-8 text-center">
          <div class="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-green-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Agendamento Confirmado!</h3>
          <p class="text-sm text-gray-500 mb-4">{schedulingResult?.message || 'Voce recebera uma confirmacao em breve.'}</p>

          <div class="bg-green-50 border border-green-200 rounded-xl p-4 text-left space-y-2 mb-4">
            <div class="flex justify-between">
              <span class="text-xs text-green-700">Data</span>
              <span class="text-sm font-semibold text-green-900 capitalize">{formatDateBR(selectedDate)}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-xs text-green-700">Horario</span>
              <span class="text-sm font-semibold text-green-900">{selectedTime}</span>
            </div>
          </div>

          <p class="text-xs text-gray-400">Obrigado, {clientData.name}!</p>
        </div>
      {/if}

    {/if}
  </div>
</div>
