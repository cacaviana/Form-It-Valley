<script lang="ts">
  import { onMount } from 'svelte';
  import { authFetch } from '$lib/utils/auth-fetch';

  interface QualifyingAnswer {
    node_id?: string;
    question?: string;
    value?: string;
    label?: string;
  }

  interface Scheduling {
    id: string;
    lead_name: string;
    lead_email: string;
    lead_phone: string;
    lead_address?: string;
    scheduled_date: string;
    scheduled_time: string;
    status: string;
    flow_slug: string;
    qualifying_answers?: QualifyingAnswer[];
    gcal_event_link: string | null;
    email_sent: boolean;
    whatsapp_sent: boolean;
    created_at: string;
  }

  interface DateSlot {
    date: string;
    available: boolean;
    slots_count: number;
  }

  let schedulings = $state<Scheduling[]>([]);
  let dates = $state<DateSlot[]>([]);
  let loading = $state(true);
  let selected = $state<Scheduling | null>(null);

  let calMonth = $state(new Date().getMonth());
  let calYear = $state(new Date().getFullYear());
  let selectedDay = $state<string | null>(null);

  const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
  const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

  function toggleDay(date: string) {
    selectedDay = selectedDay === date ? null : date;
  }

  function clearDayFilter() {
    selectedDay = null;
  }

  onMount(async () => {
    await Promise.all([loadSchedulings(), loadDates()]);
    loading = false;
  });

  async function loadSchedulings() {
    try {
      const res = await authFetch(`/api/scheduling?month=${calMonth + 1}&year=${calYear}`);
      if (res.ok) schedulings = await res.json();
    } catch (e) { /* silent */ }
  }

  async function loadDates() {
    try {
      const res = await fetch(`/api/scheduling?action=dates&month=${calMonth + 1}&year=${calYear}`);
      if (res.ok) dates = await res.json();
    } catch (e) { /* silent */ }
  }

  async function prevMonth() {
    if (calMonth === 0) { calMonth = 11; calYear--; }
    else calMonth--;
    selectedDay = null;
    await Promise.all([loadDates(), loadSchedulings()]);
  }

  async function nextMonth() {
    if (calMonth === 11) { calMonth = 0; calYear++; }
    else calMonth++;
    selectedDay = null;
    await Promise.all([loadDates(), loadSchedulings()]);
  }

  function formatDate(dateStr: string): string {
    if (!dateStr) return '-';
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function formatDateTime(iso: string): string {
    try {
      return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
    } catch { return iso; }
  }

  // Agrupar datas do calendario em semanas
  function getCalendarWeeks(dateSlots: DateSlot[]): (DateSlot | null)[][] {
    if (dateSlots.length === 0) return [];
    const firstDay = new Date(calYear, calMonth, 1).getDay();
    const weeks: (DateSlot | null)[][] = [];
    let week: (DateSlot | null)[] = Array(firstDay).fill(null);
    for (const ds of dateSlots) {
      week.push(ds);
      if (week.length === 7) { weeks.push(week); week = []; }
    }
    if (week.length > 0) { while (week.length < 7) week.push(null); weeks.push(week); }
    return weeks;
  }

  let weeks = $derived(getCalendarWeeks(dates));

  let today = $derived(new Date().toISOString().split('T')[0]);

  // Agendamentos filtrados pelo mes selecionado
  let schedulingsDoMes = $derived(schedulings.filter(s => {
    const [y, m] = s.scheduled_date.split('-').map(Number);
    return y === calYear && m === calMonth + 1;
  }));
  let agendadosNoMes = $derived(schedulingsDoMes.length);

  // Agendados daqui pra frente (no mes selecionado)
  let agendadosFuturos = $derived(schedulings.filter(s => {
    const [y, m] = s.scheduled_date.split('-').map(Number);
    return y === calYear && m === calMonth + 1 && s.scheduled_date >= today;
  }).length);

  // Lista visivel na tabela — filtra por dia se selectedDay estiver setado
  let schedulingsFiltrados = $derived(
    selectedDay
      ? schedulingsDoMes.filter(s => s.scheduled_date === selectedDay)
      : schedulingsDoMes
  );

  function formatDayLabel(dateStr: string): string {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long' });
  }

  const bookingStatusColors: Record<string, string> = {
    confirmed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    completed: 'bg-blue-100 text-blue-800'
  };
  const bookingStatusLabels: Record<string, string> = {
    confirmed: 'Confirmado',
    cancelled: 'Cancelado',
    completed: 'Concluído'
  };
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex justify-between items-center">
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-bold text-gray-900">Agendamentos</h1>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Carregando...</div>
    {:else}
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Calendario de disponibilidade -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl border p-5">
            <div class="flex items-center justify-between mb-4">
              <button onclick={prevMonth} class="p-1 hover:bg-gray-100 rounded cursor-pointer">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
              </button>
              <h3 class="text-sm font-semibold text-gray-900">{monthNames[calMonth]} {calYear}</h3>
              <button onclick={nextMonth} class="p-1 hover:bg-gray-100 rounded cursor-pointer">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
              </button>
            </div>

            <!-- Dias da semana -->
            <div class="grid grid-cols-7 gap-0 mb-1">
              {#each dayNames as day}
                <div class="text-center text-[10px] font-semibold text-gray-400 uppercase py-1">{day}</div>
              {/each}
            </div>

            <!-- Calendario -->
            {#each weeks as week}
              <div class="grid grid-cols-7 gap-0">
                {#each week as cell}
                  {#if cell}
                    {@const dayNum = parseInt(cell.date.split('-')[2])}
                    {@const hasBookings = schedulingsDoMes.some(s => s.scheduled_date === cell.date)}
                    {@const isSelected = selectedDay === cell.date}
                    <button
                      type="button"
                      onclick={() => toggleDay(cell.date)}
                      class="aspect-square flex items-center justify-center text-xs rounded-lg m-0.5 transition-all cursor-pointer
                        {cell.available ? 'bg-green-50 text-green-800 font-medium hover:bg-green-100' : 'text-gray-300 hover:bg-gray-50'}
                        {hasBookings ? 'ring-1 ring-blue-300' : ''}
                        {isSelected ? '!bg-blue-600 !text-white !ring-2 !ring-blue-700 font-bold' : ''}"
                      title={cell.available ? `${cell.slots_count} horários livres${hasBookings ? ' · clique para filtrar agendamentos' : ''}` : (hasBookings ? 'Clique para filtrar agendamentos' : 'Indisponível')}
                    >
                      {dayNum}
                      {#if cell.available && cell.slots_count > 0 && !isSelected}
                        <span class="text-[8px] text-green-500 ml-0.5">{cell.slots_count}</span>
                      {/if}
                    </button>
                  {:else}
                    <div class="aspect-square"></div>
                  {/if}
                {/each}
              </div>
            {/each}

            <div class="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] text-gray-400">
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-green-200"></span> Disponível</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-gray-200"></span> Indisponível</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded ring-1 ring-blue-300"></span> Com agendamento</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-blue-600"></span> Selecionado</span>
            </div>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-2 gap-3 mt-4">
            <div class="bg-white rounded-xl border p-4 text-center">
              <p class="text-2xl font-bold text-blue-600">{agendadosNoMes}</p>
              <p class="text-xs font-medium text-gray-700">Agendados no mes</p>
              <p class="text-[10px] text-gray-400 mt-0.5">Total de agendamentos do mes selecionado</p>
            </div>
            <div class="bg-white rounded-xl border p-4 text-center">
              <p class="text-2xl font-bold text-purple-600">{agendadosFuturos}</p>
              <p class="text-xs font-medium text-gray-700">Agendados daqui pra frente</p>
              <p class="text-[10px] text-gray-400 mt-0.5">Agendamentos de hoje em diante no mes</p>
            </div>
          </div>
        </div>

        <!-- Lista de agendamentos -->
        <div class="lg:col-span-2">
          <div class="flex items-center justify-between mb-3 gap-3 flex-wrap">
            <h2 class="text-sm font-semibold text-gray-400 uppercase tracking-wider">Agendamentos realizados</h2>
            {#if selectedDay}
              <div class="flex items-center gap-2">
                <span class="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full font-medium capitalize">
                  Filtrando: {formatDayLabel(selectedDay)}
                </span>
                <button onclick={clearDayFilter} class="text-xs text-gray-500 hover:text-gray-800 cursor-pointer underline">
                  Limpar filtro
                </button>
              </div>
            {/if}
          </div>

          {#if schedulingsDoMes.length === 0}
            <div class="bg-white rounded-xl border p-8 text-center">
              <p class="text-gray-500 text-sm">Nenhum agendamento realizado ainda.</p>
              <p class="text-xs text-gray-400 mt-1">Os agendamentos aparecerão aqui quando leads preencherem os formulários.</p>
            </div>
          {:else if schedulingsFiltrados.length === 0}
            <div class="bg-white rounded-xl border p-8 text-center">
              <p class="text-gray-500 text-sm">Nenhum agendamento neste dia.</p>
              <button onclick={clearDayFilter} class="text-xs text-blue-600 hover:underline mt-2 cursor-pointer">Ver todos do mês</button>
            </div>
          {:else}
            <div class="bg-white rounded-xl border overflow-hidden">
              <table class="w-full">
                <thead>
                  <tr class="border-b bg-gray-50">
                    <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Lead</th>
                    <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Data / Hora</th>
                    <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                    <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Notificações</th>
                    <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Respostas</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  {#each schedulingsFiltrados as s}
                    <tr class="hover:bg-gray-50 transition-colors">
                      <td class="px-4 py-3">
                        <p class="font-medium text-gray-900 text-sm">{s.lead_name}</p>
                        <p class="text-xs text-gray-500">{s.lead_email}</p>
                        {#if s.lead_phone}<p class="text-xs text-gray-400">{s.lead_phone}</p>{/if}
                      </td>
                      <td class="px-4 py-3">
                        <p class="text-sm text-gray-900">{formatDate(s.scheduled_date)}</p>
                        <p class="text-xs text-gray-500">{s.scheduled_time}</p>
                      </td>
                      <td class="px-4 py-3">
                        <span class="text-xs px-2 py-0.5 rounded-full {bookingStatusColors[s.status] || 'bg-gray-100 text-gray-600'}">
                          {bookingStatusLabels[s.status] || s.status}
                        </span>
                      </td>
                      <td class="px-4 py-3">
                        <div class="flex gap-1.5">
                          {#if s.gcal_event_link}
                            <a href={s.gcal_event_link} target="_blank" class="text-[10px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded" title="Google Calendar">GCal</a>
                          {/if}
                          {#if s.email_sent}
                            <span class="text-[10px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">Email</span>
                          {/if}
                          {#if s.whatsapp_sent}
                            <span class="text-[10px] bg-green-50 text-green-600 px-1.5 py-0.5 rounded">WhatsApp</span>
                          {/if}
                        </div>
                      </td>
                      <td class="px-4 py-3">
                        {#if s.qualifying_answers && s.qualifying_answers.length > 0}
                          <button
                            onclick={() => selected = s}
                            class="text-xs text-blue-600 hover:text-blue-800 hover:underline cursor-pointer font-medium"
                          >
                            Ver respostas ({s.qualifying_answers.length})
                          </button>
                        {:else}
                          <span class="text-xs text-gray-300">-</span>
                        {/if}
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {/if}
        </div>

      </div>
    {/if}
  </main>
</div>

<!-- Modal: respostas do lead -->
{#if selected}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    onclick={() => selected = null}
    role="presentation"
  >
    <div
      class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[85vh] overflow-hidden flex flex-col"
      onclick={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
    >
      <div class="flex items-start justify-between px-6 py-4 border-b">
        <div>
          <h3 class="text-base font-bold text-gray-900">{selected.lead_name}</h3>
          <p class="text-xs text-gray-500">{selected.lead_email}</p>
          <p class="text-xs text-gray-400">{formatDate(selected.scheduled_date)} as {selected.scheduled_time}</p>
        </div>
        <button onclick={() => selected = null} class="text-gray-400 hover:text-gray-700 cursor-pointer p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <div class="px-6 py-4 overflow-y-auto">
        <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Respostas do lead</h4>
        {#if selected.qualifying_answers && selected.qualifying_answers.length > 0}
          <div class="space-y-3">
            {#each selected.qualifying_answers as ans, i}
              <div class="border-l-2 border-blue-100 pl-3">
                <p class="text-xs text-gray-500">{ans.question || `Pergunta ${i + 1}`}</p>
                <p class="text-sm font-medium text-gray-900">{ans.label || ans.value || '-'}</p>
              </div>
            {/each}
          </div>
        {:else}
          <p class="text-sm text-gray-500">Nenhuma resposta registrada.</p>
        {/if}
      </div>

      <div class="px-6 py-3 border-t flex justify-end">
        <button onclick={() => selected = null} class="text-sm text-gray-600 hover:text-gray-900 px-4 py-2 cursor-pointer">Fechar</button>
      </div>
    </div>
  </div>
{/if}
