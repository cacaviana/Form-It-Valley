<script lang="ts">
  import type { SchedulingConfig, SchedulingDateEntry } from '$lib/dto/flows/types';
  import { authFetch } from '$lib/utils/auth-fetch';

  let {
    open,
    value,
    meetingLinkOverride = null,
    onSave,
    onCancel
  } = $props<{
    open: boolean;
    value: SchedulingConfig | null;
    meetingLinkOverride?: string | null;
    onSave: (payload: { schedulingConfig: SchedulingConfig | null; meetingLinkOverride: string | null }) => void;
    onCancel: () => void;
  }>();

  const AVAILABLE_TIMES = [
    '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
    '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
    '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'
  ];

  const MONTH_NAMES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
  const DAY_NAMES = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];

  // ── Estado local (descarta no cancelar) ──
  let useGlobal = $state(value === null);
  let localDates = $state<SchedulingDateEntry[]>([]);
  let maxBookings = $state(1);

  // ── Link da reunião ──
  let linkMode = $state<'meet' | 'custom'>('meet');
  let localLink = $state('');

  let globalSummary = $state('Carregando configuração global...');
  let calMonth = $state(new Date().getMonth());
  let calYear = $state(new Date().getFullYear());

  $effect(() => {
    // Ler props ANTES do early return pra garantir que sao rastreadas como deps reativas
    const _value = value;
    const _link = meetingLinkOverride;
    if (!open) return;

    // Computar tudo em vars locais (sem ler state que sera escrito)
    const safeDates = Array.isArray(_value?.dates) ? structuredClone(_value.dates) : [];
    const trimmed = _link?.trim() || '';

    useGlobal = _value == null;
    localDates = safeDates;
    maxBookings = _value?.max_bookings_per_slot ?? 1;
    linkMode = trimmed ? 'custom' : 'meet';
    localLink = trimmed;

    if (safeDates.length > 0) {
      const first = safeDates[0].date;
      calYear = parseInt(first.slice(0, 4));
      calMonth = parseInt(first.slice(5, 7)) - 1;
    } else {
      const now = new Date();
      calMonth = now.getMonth();
      calYear = now.getFullYear();
    }
    loadGlobal();
  });

  async function loadGlobal() {
    try {
      const res = await authFetch('/api/scheduling-config');
      if (res.ok) {
        const g = await res.json();
        globalSummary = `${g.morning_slots ?? 3} de manhã + ${g.afternoon_slots ?? 3} de tarde, até ${g.max_bookings_per_slot ?? 1} por horário`;
      }
    } catch { globalSummary = 'configuração padrão'; }
  }

  // ── Manipulação de datas ──
  function dateKey(y: number, m: number, d: number): string {
    return `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  }

  function isDateSelected(dateStr: string): boolean {
    return localDates.some(d => d.date === dateStr);
  }

  function toggleDate(dateStr: string) {
    if (isDateSelected(dateStr)) {
      localDates = localDates.filter(d => d.date !== dateStr);
    } else {
      // Default: nenhum horário marcado — admin escolhe
      localDates = [...localDates, { date: dateStr, times: [] }].sort((a, b) => a.date.localeCompare(b.date));
    }
  }

  function toggleTime(dateStr: string, time: string) {
    localDates = localDates.map(d => {
      if (d.date !== dateStr) return d;
      const has = d.times.includes(time);
      const times = has ? d.times.filter(t => t !== time) : [...d.times, time].sort();
      return { ...d, times };
    });
  }

  function removeDate(dateStr: string) {
    localDates = localDates.filter(d => d.date !== dateStr);
  }

  function applyToAll(times: string[]) {
    localDates = localDates.map(d => ({ ...d, times: [...times].sort() }));
  }

  // ── Calendário ──
  function prevMonth() {
    if (calMonth === 0) { calMonth = 11; calYear -= 1; }
    else calMonth -= 1;
  }
  function nextMonth() {
    if (calMonth === 11) { calMonth = 0; calYear += 1; }
    else calMonth += 1;
  }

  let calendarGrid = $derived.by(() => {
    const firstDay = new Date(calYear, calMonth, 1).getDay();
    const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const cells: ({ day: number; date: string; isPast: boolean } | null)[] = [];
    for (let i = 0; i < firstDay; i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(calYear, calMonth, d);
      cells.push({
        day: d,
        date: dateKey(calYear, calMonth, d),
        isPast: date < today
      });
    }
    while (cells.length % 7 !== 0) cells.push(null);
    return cells;
  });

  // ── Formatação ──
  function formatDate(dateStr: string): string {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: 'short' });
  }

  // ── Validação e save ──
  let validation = $derived.by(() => {
    if (linkMode === 'custom') {
      const trimmed = localLink.trim();
      if (!trimmed) return { ok: false, msg: 'Informe a URL do link personalizado da reunião.' };
      if (!/^https?:\/\//i.test(trimmed)) return { ok: false, msg: 'O link deve começar com http:// ou https://' };
    }
    if (useGlobal) return { ok: true, msg: '' };
    if (localDates.length === 0) return { ok: false, msg: 'Selecione pelo menos uma data no calendário.' };
    const withoutTimes = localDates.filter(d => d.times.length === 0);
    if (withoutTimes.length > 0) {
      return { ok: false, msg: `${withoutTimes.length} data(s) sem horário escolhido — marque ao menos 1 horário por data.` };
    }
    return { ok: true, msg: '' };
  });

  function save() {
    if (!validation.ok) return;
    const schedulingPayload: SchedulingConfig | null = useGlobal
      ? null
      : {
          dates: localDates,
          max_bookings_per_slot: Math.max(1, maxBookings)
        };
    const linkPayload = linkMode === 'custom' ? localLink.trim() : null;
    onSave({ schedulingConfig: schedulingPayload, meetingLinkOverride: linkPayload });
  }

  function toggleUseGlobal() {
    useGlobal = !useGlobal;
  }

  let totalSlots = $derived(localDates.reduce((sum, d) => sum + d.times.length, 0));
</script>

{#if open}
  <div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-stretch md:items-center justify-center p-0 md:p-6">
    <div class="bg-white w-full md:max-w-5xl md:rounded-2xl shadow-2xl flex flex-col max-h-screen overflow-hidden">

      <!-- Header -->
      <div class="px-5 py-3 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
        <div>
          <h2 class="text-base font-semibold text-gray-900">Horários deste formulário</h2>
          <p class="text-xs text-gray-500">Escolha datas e horários específicos, ou use a configuração global</p>
        </div>
        <button onclick={onCancel} class="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-400 hover:text-gray-700 cursor-pointer transition-colors" aria-label="Fechar">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto p-5 space-y-5">

        <!-- Link da reunião -->
        <div class="bg-violet-50/40 border border-violet-100 rounded-xl p-4 space-y-3">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-violet-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
            </svg>
            <span class="text-sm font-semibold text-violet-900">Link da reunião enviado ao lead</span>
          </div>

          <label class="flex items-start gap-2 cursor-pointer">
            <input
              type="radio"
              name="link-mode"
              value="meet"
              checked={linkMode === 'meet'}
              onchange={() => (linkMode = 'meet')}
              class="mt-0.5 accent-violet-600"
            />
            <div class="flex-1">
              <div class="text-sm text-gray-800 font-medium">Gerar link do Google Meet automaticamente</div>
              <p class="text-xs text-gray-500">Cada agendamento cria uma sala Meet única no evento do Calendar.</p>
            </div>
          </label>

          <label class="flex items-start gap-2 cursor-pointer">
            <input
              type="radio"
              name="link-mode"
              value="custom"
              checked={linkMode === 'custom'}
              onchange={() => (linkMode = 'custom')}
              class="mt-0.5 accent-violet-600"
            />
            <div class="flex-1">
              <div class="text-sm text-gray-800 font-medium">Usar link personalizado</div>
              <p class="text-xs text-gray-500 mb-2">Mesmo link enviado a todos os leads deste formulário (Zoom, sala fixa, etc).</p>
              {#if linkMode === 'custom'}
                <input
                  type="url"
                  bind:value={localLink}
                  placeholder="https://meet.google.com/abc-defg-hij ou https://zoom.us/..."
                  class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm bg-white outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
                />
              {/if}
            </div>
          </label>
        </div>

        <!-- Toggle global -->
        <div class="flex items-start gap-3 bg-gray-50 border border-gray-200 rounded-xl p-4">
          <button
            type="button"
            onclick={toggleUseGlobal}
            class="relative inline-flex items-center flex-shrink-0 h-6 w-11 rounded-full transition-colors cursor-pointer mt-0.5 {useGlobal ? 'bg-blue-600' : 'bg-gray-300'}"
            role="switch"
            aria-checked={useGlobal}
            aria-label="Usar configuração global"
          >
            <span class="inline-block w-4 h-4 bg-white rounded-full shadow transform transition-transform {useGlobal ? 'translate-x-6' : 'translate-x-1'}"></span>
          </button>
          <div class="flex-1">
            <div class="text-sm font-semibold text-gray-800">Usar configuração global</div>
            <p class="text-xs text-gray-500 mt-0.5">Atualmente: {globalSummary}</p>
          </div>
        </div>

        {#if !useGlobal}
          <div class="grid md:grid-cols-[320px_1fr] gap-5">

            <!-- COLUNA ESQUERDA — calendário + multibooking -->
            <div class="space-y-4">
              <!-- Calendário -->
              <div class="bg-white border border-gray-200 rounded-xl p-4">
                <div class="flex items-center justify-between mb-3">
                  <button type="button" onclick={prevMonth} class="w-7 h-7 rounded hover:bg-gray-100 flex items-center justify-center text-gray-500 cursor-pointer" aria-label="Mês anterior">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
                  </button>
                  <span class="text-sm font-semibold text-gray-700">{MONTH_NAMES[calMonth]} {calYear}</span>
                  <button type="button" onclick={nextMonth} class="w-7 h-7 rounded hover:bg-gray-100 flex items-center justify-center text-gray-500 cursor-pointer" aria-label="Próximo mês">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
                  </button>
                </div>
                <div class="grid grid-cols-7 gap-1 text-center text-[10px] text-gray-400 font-medium mb-1">
                  {#each DAY_NAMES as dn}<div>{dn}</div>{/each}
                </div>
                <div class="grid grid-cols-7 gap-1">
                  {#each calendarGrid as cell}
                    {#if cell}
                      {@const selected = isDateSelected(cell.date)}
                      <button
                        type="button"
                        disabled={cell.isPast}
                        onclick={() => toggleDate(cell.date)}
                        class="aspect-square text-xs rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed
                          {cell.isPast ? 'text-gray-300' : selected ? 'bg-blue-600 text-white font-semibold' : 'text-gray-700 hover:bg-blue-50'}"
                      >
                        {cell.day}
                      </button>
                    {:else}
                      <div></div>
                    {/if}
                  {/each}
                </div>
              </div>

              <!-- Multibooking -->
              <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                <label for="max-bookings-input" class="block text-xs font-semibold text-emerald-900 mb-2 uppercase tracking-wide">
                  Leads por horário
                </label>
                <div class="flex items-center gap-3">
                  <input
                    id="max-bookings-input"
                    type="number"
                    min="1"
                    max="20"
                    bind:value={maxBookings}
                    class="w-20 border border-emerald-200 bg-white rounded-lg px-3 py-2 text-xl font-bold text-emerald-700 text-center focus:ring-2 focus:ring-emerald-500/25 focus:border-emerald-400 outline-none"
                  />
                  <p class="text-xs text-emerald-700 flex-1">
                    {maxBookings <= 1 ? 'Apenas 1 lead por horário.' : `Até ${maxBookings} leads no mesmo horário.`}
                  </p>
                </div>
              </div>

              <!-- Resumo -->
              <div class="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-700">
                <p><strong>{localDates.length}</strong> data{localDates.length !== 1 ? 's' : ''} selecionada{localDates.length !== 1 ? 's' : ''}</p>
                <p><strong>{totalSlots}</strong> horário{totalSlots !== 1 ? 's' : ''} no total · até {maxBookings} lead{maxBookings > 1 ? 's' : ''} por horário</p>
              </div>
            </div>

            <!-- COLUNA DIREITA — datas selecionadas com horários -->
            <div class="space-y-2">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                  Horários por data ({localDates.length})
                </span>
                {#if localDates.length > 1}
                  <button
                    type="button"
                    onclick={() => applyToAll(localDates[0]?.times || [])}
                    class="text-[11px] text-blue-600 hover:text-blue-800 underline cursor-pointer"
                    title="Aplicar os horários da 1ª data em todas as demais"
                  >
                    Aplicar 1ª data em todas
                  </button>
                {/if}
              </div>

              {#if localDates.length === 0}
                <div class="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center text-sm text-blue-700">
                  Clique em datas no calendário ao lado para começar.
                </div>
              {:else}
                <div class="space-y-2 max-h-[420px] overflow-y-auto pr-1">
                  {#each localDates as entry (entry.date)}
                    <div class="border border-gray-200 rounded-xl p-3 bg-white">
                      <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-semibold text-gray-800 capitalize">{formatDate(entry.date)}</span>
                        <button
                          type="button"
                          onclick={() => removeDate(entry.date)}
                          class="text-gray-300 hover:text-red-500 cursor-pointer"
                          aria-label="Remover data"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                        </button>
                      </div>
                      <div class="grid grid-cols-7 gap-1.5">
                        {#each AVAILABLE_TIMES as time}
                          {@const checked = entry.times.includes(time)}
                          <button
                            type="button"
                            onclick={() => toggleTime(entry.date, time)}
                            class="px-1 py-1 text-[11px] rounded font-medium cursor-pointer transition-colors
                              {checked ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}"
                          >
                            {time}
                          </button>
                        {/each}
                      </div>
                      {#if entry.times.length === 0}
                        <p class="text-[11px] text-amber-600 mt-2">⚠ Nenhum horário escolhido — marque ao menos 1</p>
                      {/if}
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="px-5 py-3 border-t border-gray-200 flex items-center justify-end gap-3 flex-shrink-0 bg-white">
        {#if !validation.ok}
          <span class="text-xs text-amber-600 mr-auto">{validation.msg}</span>
        {/if}
        <button
          type="button"
          onclick={onCancel}
          class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors"
        >
          Cancelar
        </button>
        <button
          type="button"
          onclick={save}
          disabled={!validation.ok}
          class="px-4 py-2 text-sm font-semibold text-white rounded-lg cursor-pointer transition-colors bg-blue-600 hover:bg-blue-700 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Salvar
        </button>
      </div>
    </div>
  </div>
{/if}
