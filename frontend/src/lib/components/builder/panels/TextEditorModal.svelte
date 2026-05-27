<script lang="ts">
  import type { UITexts } from '$lib/dto/flows/types';
  import { UI_TEXT_DEFAULTS, interpolate } from '$lib/dto/flows/uiTextDefaults';

  type SectionDef = { section: string; items: { key: keyof UITexts; label: string }[] };

  let {
    open,
    title,
    value,
    sections,
    themeColor = 'violet',
    onSave,
    onCancel
  } = $props<{
    open: boolean;
    title: string;
    value: UITexts | null;
    sections: SectionDef[];
    themeColor?: string;
    onSave: (next: UITexts | null) => void;
    onCancel: () => void;
  }>();

  const themeColorMap: Record<string, { main: string; gradient: string; gradientHeader: string }> = {
    violet:  { main: '#7C3AED', gradient: 'linear-gradient(135deg, #7C3AED, #9333EA)', gradientHeader: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' },
    blue:    { main: '#2563EB', gradient: 'linear-gradient(135deg, #2563EB, #3B82F6)', gradientHeader: 'linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)' },
    emerald: { main: '#059669', gradient: 'linear-gradient(135deg, #059669, #10B981)', gradientHeader: 'linear-gradient(135deg, #059669 0%, #10B981 100%)' },
    rose:    { main: '#E11D48', gradient: 'linear-gradient(135deg, #E11D48, #F43F5E)', gradientHeader: 'linear-gradient(135deg, #E11D48 0%, #F43F5E 100%)' },
    orange:  { main: '#EA580C', gradient: 'linear-gradient(135deg, #EA580C, #F97316)', gradientHeader: 'linear-gradient(135deg, #EA580C 0%, #F97316 100%)' },
    cyan:    { main: '#0891B2', gradient: 'linear-gradient(135deg, #0891B2, #06B6D4)', gradientHeader: 'linear-gradient(135deg, #0891B2 0%, #06B6D4 100%)' },
    amber:   { main: '#D97706', gradient: 'linear-gradient(135deg, #D97706, #F59E0B)', gradientHeader: 'linear-gradient(135deg, #D97706 0%, #F59E0B 100%)' },
    red:     { main: '#DC2626', gradient: 'linear-gradient(135deg, #DC2626, #EF4444)', gradientHeader: 'linear-gradient(135deg, #DC2626 0%, #EF4444 100%)' },
    slate:   { main: '#334155', gradient: 'linear-gradient(135deg, #334155, #475569)', gradientHeader: 'linear-gradient(135deg, #334155 0%, #475569 100%)' }
  };
  function buildCustomTheme(hex: string) {
    return {
      main: hex,
      gradient: `linear-gradient(135deg, ${hex}, ${hex}CC)`,
      gradientHeader: `linear-gradient(135deg, ${hex} 0%, ${hex}CC 100%)`
    };
  }
  let theme = $derived(
    themeColorMap[themeColor] ||
    (/^#[0-9a-fA-F]{6}$/.test(themeColor) ? buildCustomTheme(themeColor) : themeColorMap.violet)
  );

  // Dados sample para o preview
  const SAMPLE = {
    nome: 'Henrique',
    email: 'henrique@example.com',
    data: 'quinta-feira, 28 de maio de 2026',
    horario: '10:00',
    telefone: '+55 (11) 99999-9999',
    current: 1,
    total: 5
  };

  // Estado local: copia das chaves dessas sections
  let local = $state<Record<string, string>>({});
  let activeIndex = $state(0);

  let allKeysHere = $derived<string[]>(sections.flatMap(s => s.items.map(i => i.key as string)));

  $effect(() => {
    const _value = value;
    const _sections = sections;
    if (!open) return;
    const next: Record<string, string> = {};
    for (const sec of _sections) {
      for (const it of sec.items) {
        const k = it.key as string;
        const v = _value?.[it.key];
        next[k] = typeof v === 'string' ? v : '';
      }
    }
    local = next;
    activeIndex = 0;
  });

  function getDefault(key: string): string {
    return (UI_TEXT_DEFAULTS as Record<string, string>)[key] ?? '';
  }

  function resolved(key: string): string {
    const v = local[key]?.trim();
    return v && v.length > 0 ? v : getDefault(key);
  }

  function resolvedI(key: string): string {
    return interpolate(resolved(key), SAMPLE);
  }

  function isCustomized(key: string): boolean {
    return local[key]?.length > 0 && local[key] !== getDefault(key);
  }

  function restoreDefault(key: string) {
    local = { ...local, [key]: '' };
  }

  function restoreAll() {
    const next: Record<string, string> = { ...local };
    for (const k of allKeysHere) next[k] = '';
    local = next;
  }

  function save() {
    const merged: UITexts = { ...(value || {}) };
    let hasAny = false;
    for (const k of allKeysHere) {
      const v = local[k]?.trim();
      if (v && v.length > 0) {
        (merged as Record<string, string>)[k] = v;
        hasAny = true;
      } else {
        delete (merged as Record<string, string>)[k];
      }
    }
    const outsideKeys = Object.keys(merged).filter(k => !allKeysHere.includes(k));
    if (!hasAny && outsideKeys.length === 0) {
      onSave(null);
    } else {
      onSave(merged);
    }
  }

  // Inferir tipo de preview pela seção ativa
  let activeSection = $derived(sections[activeIndex]);
  let activePreviewKind = $derived.by(() => {
    const firstKey = activeSection?.items[0]?.key as string | undefined;
    if (!firstKey) return '';
    if (firstKey.startsWith('form_')) return 'form';
    if (firstKey.startsWith('questions_')) return 'questions';
    if (firstKey.startsWith('calendar_')) return 'calendar';
    if (firstKey.startsWith('time_')) return 'time';
    if (firstKey.startsWith('confirm_')) return 'confirm';
    if (firstKey.startsWith('done_')) return 'done';
    return '';
  });
</script>

{#if open}
  <div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-stretch md:items-center justify-center p-0 md:p-6">
    <div class="bg-white w-full md:max-w-6xl md:rounded-2xl shadow-2xl flex flex-col max-h-screen overflow-hidden">

      <!-- Header -->
      <div class="px-5 py-3 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
        <div>
          <h2 class="text-base font-semibold text-gray-900">{title}</h2>
          <p class="text-xs text-gray-500">Edite os textos à esquerda e veja o preview em tempo real à direita. Placeholders: <code class="text-blue-600">{`{{nome}}`}</code> <code class="text-blue-600">{`{{email}}`}</code> <code class="text-blue-600">{`{{data}}`}</code> <code class="text-blue-600">{`{{horario}}`}</code> <code class="text-blue-600">{`{{telefone}}`}</code></p>
        </div>
        <button onclick={onCancel} class="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-400 hover:text-gray-700 cursor-pointer transition-colors" aria-label="Fechar">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 bg-gray-50 px-3 py-2 flex gap-1 overflow-x-auto flex-shrink-0">
        {#each sections as section, i}
          <button
            type="button"
            onclick={() => (activeIndex = i)}
            class="px-3 py-1.5 text-xs font-semibold rounded-lg cursor-pointer transition-colors whitespace-nowrap
              {activeIndex === i ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-200'}"
          >
            {section.section}
          </button>
        {/each}
        <div class="flex-1"></div>
        <button type="button" onclick={restoreAll} class="text-[11px] text-blue-600 hover:text-blue-800 underline cursor-pointer self-center">
          Restaurar todos os padrões
        </button>
      </div>

      <!-- Body 2 colunas -->
      <div class="flex-1 flex flex-col md:flex-row overflow-hidden">
        <!-- Esquerda: inputs da seção ativa -->
        <aside class="w-full md:w-[400px] flex-shrink-0 border-r border-gray-200 overflow-y-auto bg-gray-50/40">
          <div class="p-5 space-y-3">
            {#if activeSection}
              {#each activeSection.items as item}
                {@const k = item.key as string}
                {@const def = getDefault(k)}
                <div>
                  <div class="flex items-center justify-between mb-1">
                    <label for={`txt-${k}`} class="text-xs font-medium text-gray-700">{item.label}</label>
                    {#if isCustomized(k)}
                      <button type="button" onclick={() => restoreDefault(k)} class="text-[10px] text-blue-600 hover:text-blue-800 underline cursor-pointer">
                        Restaurar padrão
                      </button>
                    {/if}
                  </div>
                  <input
                    id={`txt-${k}`}
                    type="text"
                    value={local[k] ?? ''}
                    oninput={(e) => (local = { ...local, [k]: (e.target as HTMLInputElement).value })}
                    placeholder={def}
                    class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  />
                  {#if !local[k]}
                    <p class="text-[10px] text-gray-400 mt-0.5 truncate">Padrão: <span class="font-mono">{def}</span></p>
                  {/if}
                </div>
              {/each}
            {/if}
          </div>
        </aside>

        <!-- Direita: preview -->
        <main class="flex-1 overflow-y-auto bg-gray-100">
          <div class="px-4 py-3 border-b border-gray-200 bg-white flex items-center gap-2 sticky top-0 z-10">
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            <span class="text-xs font-medium text-gray-600 uppercase tracking-wide">Preview — {activeSection?.section ?? ''}</span>
          </div>

          <div class="p-6 flex items-start justify-center bg-gray-900/80 min-h-full" style="--tc: {theme.main};">
            <div class="max-w-[420px] w-full">

              {#if activePreviewKind === 'form'}
                {@render formPreview()}
              {:else if activePreviewKind === 'questions'}
                {@render questionsPreview()}
              {:else if activePreviewKind === 'calendar'}
                {@render calendarPreview()}
              {:else if activePreviewKind === 'time'}
                {@render timePreview()}
              {:else if activePreviewKind === 'confirm'}
                {@render confirmPreview()}
              {:else if activePreviewKind === 'done'}
                {@render donePreview()}
              {/if}

            </div>
          </div>
        </main>
      </div>

      <!-- Footer -->
      <div class="px-5 py-3 border-t border-gray-200 flex items-center justify-end gap-2 flex-shrink-0 bg-white">
        <button type="button" onclick={onCancel} class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors">
          Cancelar
        </button>
        <button type="button" onclick={save} class="px-4 py-2 text-sm font-semibold text-white rounded-lg cursor-pointer transition-colors bg-blue-600 hover:bg-blue-700 active:scale-[0.98]">
          Salvar
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- ============ Previews ============ -->

{#snippet formPreview()}
  <div class="bg-white rounded-2xl border border-white/50 shadow-xl overflow-hidden">
    <div class="px-6 pt-3 pb-2 text-center" style="background: {theme.gradientHeader};">
      <div class="text-white text-base font-bold py-2">IT VALLEY SCHOOL</div>
      <p class="text-[12px] text-white/85 font-light">Preencha seus dados para falar com nosso consultor</p>
    </div>
    <div class="p-5 space-y-3">
      <div>
        <span class="block text-[10px] font-semibold text-gray-500 mb-1 uppercase">{resolved('form_label_name')}</span>
        <div class="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-400">{resolved('form_placeholder_name')}</div>
      </div>
      <div>
        <span class="block text-[10px] font-semibold text-gray-500 mb-1 uppercase">{resolved('form_label_email')}</span>
        <div class="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-400">{resolved('form_placeholder_email')}</div>
      </div>
      <div>
        <span class="block text-[10px] font-semibold text-gray-500 mb-1 uppercase">{resolved('form_label_whatsapp')}</span>
        <div class="flex gap-1.5">
          <div class="border border-gray-200 bg-gray-50 rounded-lg px-2 py-2 text-xs text-gray-400 min-w-[60px]">{resolved('form_label_ddd')}</div>
          <div class="flex-1 border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-400">{resolved('form_placeholder_phone')}</div>
        </div>
      </div>
      <div class="w-full py-2.5 rounded-lg text-sm font-semibold text-white text-center" style="background: {theme.gradient};">{resolved('form_button_start')}</div>
      <p class="text-center text-[10px] text-gray-400">{resolved('form_powered_by')}</p>
    </div>
  </div>
{/snippet}

{#snippet questionsPreview()}
  <div class="bg-white rounded-2xl border border-white/50 shadow-xl overflow-hidden">
    <div class="bg-gray-100 px-4 py-3 flex items-center justify-between border-b">
      <span class="text-sm font-medium text-gray-500">{resolvedI('questions_counter')}</span>
      <div class="flex items-center gap-2">
        <div class="w-20 bg-gray-200 rounded-full h-2"><div class="h-2 rounded-full" style="width: 20%; background: {theme.gradient};"></div></div>
        <span class="text-xs text-gray-500">20%</span>
      </div>
    </div>
    <div class="p-5">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">Qual é a sua maior dificuldade?</h3>
      <div class="grid grid-cols-2 gap-2">
        <div class="border-2 border-gray-200 rounded-xl px-4 py-5 text-center text-sm font-medium text-gray-700">{resolved('questions_yes')}</div>
        <div class="border-2 border-gray-200 rounded-xl px-4 py-5 text-center text-sm font-medium text-gray-700">{resolved('questions_no')}</div>
      </div>
      <div class="flex gap-2 mt-3">
        <div class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-xs text-gray-400">{resolved('questions_placeholder_text')}</div>
        <div class="px-6 py-3 rounded-xl text-sm font-medium text-white" style="background: {theme.gradient};">{resolved('questions_button_next')}</div>
      </div>
      <p class="mt-4 text-xs text-gray-500 flex items-center gap-1">← {resolved('questions_button_back')}</p>
    </div>
  </div>
{/snippet}

{#snippet calendarPreview()}
  <div class="bg-white rounded-2xl border border-white/50 shadow-xl overflow-hidden p-4">
    <div class="text-center mb-4">
      <div class="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-2" style="background: color-mix(in srgb, {theme.main} 15%, transparent);">
        <svg class="w-5 h-5" style="color: {theme.main};" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" /></svg>
      </div>
      <h3 class="text-base font-bold text-gray-800">{resolved('calendar_title')}</h3>
      <p class="text-xs text-gray-500">{resolved('calendar_subtitle')}</p>
    </div>
    <div class="border border-gray-200 rounded-xl p-3">
      <div class="text-center text-xs font-semibold mb-2">Maio 2026</div>
      <div class="grid grid-cols-7 gap-1 text-center text-[10px] text-gray-400 mb-1">
        {#each ['D','S','T','Q','Q','S','S'] as d}<div>{d}</div>{/each}
      </div>
      <div class="grid grid-cols-7 gap-1">
        {#each [null,null,null,null,null,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31] as d}
          {#if d}
            <div class="aspect-square text-xs flex items-center justify-center rounded {d === 27 ? 'text-white font-bold' : 'text-gray-700'}" style={d === 27 ? `background: ${theme.main};` : ''}>{d}</div>
          {:else}
            <div></div>
          {/if}
        {/each}
      </div>
    </div>
    <p class="mt-3 text-xs text-gray-500 flex items-center gap-1">← {resolved('calendar_back')}</p>
  </div>
{/snippet}

{#snippet timePreview()}
  <div class="bg-white rounded-2xl border border-white/50 shadow-xl overflow-hidden p-4">
    <div class="text-center mb-4">
      <h3 class="text-base font-bold text-gray-800">{resolved('time_title')}</h3>
      <p class="text-xs text-gray-500 capitalize">{SAMPLE.data}</p>
    </div>
    <div class="mb-3">
      <p class="text-xs font-semibold text-gray-400 uppercase mb-2">{resolved('time_morning')}</p>
      <div class="grid grid-cols-3 gap-2">
        {#each ['09:00','09:30','10:00'] as t}
          <div class="py-2 rounded-xl border-2 text-xs font-semibold text-center {t === '10:00' ? 'text-white' : 'text-gray-700 border-gray-200'}" style={t === '10:00' ? `border-color: ${theme.main}; background: color-mix(in srgb, ${theme.main} 15%, transparent); color: ${theme.main};` : ''}>{t}</div>
        {/each}
      </div>
    </div>
    <div class="mb-3">
      <p class="text-xs font-semibold text-gray-400 uppercase mb-2">{resolved('time_afternoon')}</p>
      <div class="grid grid-cols-3 gap-2">
        {#each ['14:00','15:00','16:00'] as t}
          <div class="py-2 rounded-xl border-2 border-gray-200 text-xs font-semibold text-gray-700 text-center">{t}</div>
        {/each}
      </div>
    </div>
    <div class="w-full py-2.5 rounded-lg text-sm font-semibold text-white text-center mt-3" style="background: {theme.gradient};">{resolved('time_continue')}</div>
    <p class="mt-3 text-xs text-gray-400 text-center">← {resolved('time_back')}</p>
  </div>
{/snippet}

{#snippet confirmPreview()}
  <div class="bg-white rounded-2xl border border-white/50 shadow-xl overflow-hidden p-4">
    <div class="text-center mb-4">
      <h3 class="text-base font-bold text-gray-800">{resolved('confirm_title')}</h3>
      <p class="text-xs text-gray-500">{resolved('confirm_subtitle')}</p>
    </div>
    <div class="bg-gray-50 rounded-xl p-3 space-y-2 mb-4 border">
      <div class="flex justify-between text-xs"><span class="text-gray-500">{resolved('confirm_label_name')}</span><span class="font-medium">{SAMPLE.nome}</span></div>
      <div class="flex justify-between text-xs"><span class="text-gray-500">{resolved('confirm_label_email')}</span><span class="font-medium">{SAMPLE.email}</span></div>
      <div class="flex justify-between text-xs"><span class="text-gray-500">{resolved('confirm_label_phone')}</span><span class="font-medium">{SAMPLE.telefone}</span></div>
      <hr />
      <div class="flex justify-between text-xs"><span class="text-gray-500">{resolved('confirm_label_date')}</span><span class="font-medium capitalize">{SAMPLE.data}</span></div>
      <div class="flex justify-between text-xs"><span class="text-gray-500">{resolved('confirm_label_time')}</span><span class="font-medium">{SAMPLE.horario}</span></div>
    </div>
    <div class="w-full py-2.5 rounded-lg text-sm font-semibold text-white text-center" style="background: {theme.gradient};">{resolved('confirm_button')}</div>
    <p class="mt-3 text-xs text-gray-400 text-center">← {resolved('confirm_back')}</p>
  </div>
{/snippet}

{#snippet donePreview()}
  <div class="bg-white rounded-2xl border border-white/50 shadow-xl overflow-hidden p-5 text-center">
    <div class="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-3" style="background: color-mix(in srgb, {theme.main} 15%, transparent);">
      <svg class="w-7 h-7" style="color: {theme.main};" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
    </div>
    <h3 class="text-lg font-bold text-gray-800 mb-2">{resolved('done_title')}</h3>
    <p class="text-xs text-gray-500 mb-4">{resolved('done_subtitle')}</p>
    <div class="border rounded-xl p-3 text-left mb-4" style="background: color-mix(in srgb, {theme.main} 10%, transparent); border-color: color-mix(in srgb, {theme.main} 20%, transparent);">
      <div class="flex justify-between text-xs mb-1"><span style="color: {theme.main};">{resolved('confirm_label_date')}</span><span class="font-semibold capitalize">{SAMPLE.data}</span></div>
      <div class="flex justify-between text-xs"><span style="color: {theme.main};">{resolved('confirm_label_time')}</span><span class="font-semibold">{SAMPLE.horario}</span></div>
    </div>
    <div class="space-y-2 text-left mb-3">
      <div class="border rounded-lg px-3 py-2 text-[11px]" style="background: color-mix(in srgb, {theme.main} 10%, transparent); border-color: color-mix(in srgb, {theme.main} 20%, transparent); color: {theme.main};">{@html interpolate(resolved('done_gcal'), { ...SAMPLE, email: `<strong>${SAMPLE.email}</strong>` })}</div>
      <div class="border rounded-lg px-3 py-2 text-[11px]" style="background: color-mix(in srgb, {theme.main} 10%, transparent); border-color: color-mix(in srgb, {theme.main} 20%, transparent); color: {theme.main};">{@html interpolate(resolved('done_email'), { ...SAMPLE, email: `<strong>${SAMPLE.email}</strong>` })}</div>
      <div class="border rounded-lg px-3 py-2 text-[11px]" style="background: color-mix(in srgb, {theme.main} 10%, transparent); border-color: color-mix(in srgb, {theme.main} 20%, transparent); color: {theme.main};">{@html interpolate(resolved('done_whatsapp'), { ...SAMPLE, telefone: `<strong>${SAMPLE.telefone}</strong>` })}</div>
    </div>
    <p class="text-xs text-gray-500">{interpolate(resolved('done_thanks'), SAMPLE)}</p>
  </div>
{/snippet}
