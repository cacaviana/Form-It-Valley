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
  let schedulingResult = $state<{ message: string; gcal_event_link?: string; whatsapp_sent?: boolean } | null>(null);

  let resultText = $state('');

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

      await submissionService.submit(payload);
      resultText = endNode.data.message || 'Obrigado pelas suas respostas!';
    } catch (e: any) {
      resultText = 'Erro ao enviar. Tente novamente.';
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
          scheduled_time: selectedTime,
          whatsapp_template: endNode?.data.whatsappTemplate || undefined,
          whatsapp_variables: endNode?.data.whatsappVariables || undefined
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


</script>

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

      {:else}
        <div class="p-8 text-center">
          <div class="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
            <svg class="w-7 h-7 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">{endNode.data.title}</h3>
          <p class="text-sm text-gray-600">{resultText}</p>
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

          <!-- Notificacoes enviadas -->
          <div class="space-y-2 mb-4 text-left">
            {#if schedulingResult?.gcal_event_link}
              <div class="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
                <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                </svg>
                <span class="text-xs text-blue-700">Convite enviado para <strong>{clientData.email}</strong> via Google Calendar</span>
              </div>
            {/if}
            {#if schedulingResult?.whatsapp_sent}
              <div class="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
                <svg class="w-4 h-4 text-green-600 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
                  <path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.75.75 0 00.917.918l4.462-1.494A11.943 11.943 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-2.337 0-4.542-.664-6.407-1.813l-.456-.276-2.653.888.889-2.651-.277-.458A9.953 9.953 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/>
                </svg>
                <span class="text-xs text-green-700">WhatsApp enviado para <strong>{clientData.phone}</strong></span>
              </div>
            {/if}
          </div>

          <p class="text-xs text-gray-400">Obrigado, {clientData.name}!</p>
        </div>
      {/if}

    {/if}
  </div>
</div>
