<script lang="ts">
  import type { PageTemplate, PageContent } from '$lib/dto/flows/types';
  import { PAGE_TEMPLATE_OPTIONS, PAGE_PRESETS, resolvePageContent, PAGE_BACKGROUND_URL } from '$lib/dto/flows/pagePresets';
  import FormPosSidebarTop from '../../../../routes/q/[slug]/FormPosSidebarTop.svelte';
  import FormPosSidebarBottom from '../../../../routes/q/[slug]/FormPosSidebarBottom.svelte';

  let {
    open,
    themeColor,
    pageTemplate,
    pageContent,
    onSave,
    onCancel
  } = $props<{
    open: boolean;
    themeColor: string;
    pageTemplate: PageTemplate;
    pageContent: PageContent;
    onSave: (payload: { themeColor: string; pageTemplate: PageTemplate; pageContent: PageContent }) => void;
    onCancel: () => void;
  }>();

  // Cópias locais — só são commitadas no Salvar
  let localTheme = $state(themeColor);
  let localTemplate = $state<PageTemplate>(pageTemplate);
  let localContent = $state<PageContent>({ ...pageContent });

  // Toda vez que o modal abrir, ressincroniza as locais com o estado vindo de fora
  $effect(() => {
    if (open) {
      localTheme = themeColor;
      localTemplate = pageTemplate;
      localContent = { ...pageContent };
    }
  });

  const themeColors = [
    { id: 'violet', label: 'Roxo', color: '#7C3AED', main: '#7C3AED', gradientHeader: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)', gradient: 'linear-gradient(135deg, #7C3AED, #9333EA)' },
    { id: 'blue', label: 'Azul', color: '#2563EB', main: '#2563EB', gradientHeader: 'linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)', gradient: 'linear-gradient(135deg, #2563EB, #3B82F6)' },
    { id: 'emerald', label: 'Verde', color: '#059669', main: '#059669', gradientHeader: 'linear-gradient(135deg, #059669 0%, #10B981 100%)', gradient: 'linear-gradient(135deg, #059669, #10B981)' },
    { id: 'rose', label: 'Rosa', color: '#E11D48', main: '#E11D48', gradientHeader: 'linear-gradient(135deg, #E11D48 0%, #F43F5E 100%)', gradient: 'linear-gradient(135deg, #E11D48, #F43F5E)' },
    { id: 'orange', label: 'Laranja', color: '#EA580C', main: '#EA580C', gradientHeader: 'linear-gradient(135deg, #EA580C 0%, #F97316 100%)', gradient: 'linear-gradient(135deg, #EA580C, #F97316)' },
    { id: 'cyan', label: 'Ciano', color: '#0891B2', main: '#0891B2', gradientHeader: 'linear-gradient(135deg, #0891B2 0%, #06B6D4 100%)', gradient: 'linear-gradient(135deg, #0891B2, #06B6D4)' },
    { id: 'amber', label: 'Dourado', color: '#D97706', main: '#D97706', gradientHeader: 'linear-gradient(135deg, #D97706 0%, #F59E0B 100%)', gradient: 'linear-gradient(135deg, #D97706, #F59E0B)' },
    { id: 'slate', label: 'Escuro', color: '#334155', main: '#334155', gradientHeader: 'linear-gradient(135deg, #334155 0%, #475569 100%)', gradient: 'linear-gradient(135deg, #334155, #475569)' }
  ];

  let currentTheme = $derived(themeColors.find(t => t.id === localTheme) || themeColors[0]);
  let resolvedPreview = $derived(resolvePageContent(localTemplate, localContent));
  let previewBgUrl = $derived(PAGE_BACKGROUND_URL[localTemplate] || '');

  function changeTemplate(tpl: PageTemplate) {
    localTemplate = tpl;
    const preset: PageContent = PAGE_PRESETS[tpl];
    localContent = { ...preset };
  }

  function updatePageField<K extends keyof PageContent>(key: K, value: PageContent[K]) {
    localContent = { ...localContent, [key]: value };
  }

  function updateBullet(index: number, value: string) {
    const bullets = [...(resolvedPreview.bullets || [])];
    bullets[index] = value;
    updatePageField('bullets', bullets);
  }

  function updateDiscipline(index: number, value: string) {
    const disciplines = [...(resolvedPreview.disciplines || [])];
    disciplines[index] = value;
    updatePageField('disciplines', disciplines);
  }

  function restorePresetDefaults() {
    const tpl: PageTemplate = localTemplate;
    const preset: PageContent = PAGE_PRESETS[tpl];
    localContent = { ...preset };
  }

  function save() {
    onSave({ themeColor: localTheme, pageTemplate: localTemplate, pageContent: localContent });
  }
</script>

{#if open}
  <div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-stretch md:items-center justify-center p-0 md:p-6">
    <div class="bg-white w-full md:max-w-7xl md:rounded-2xl shadow-2xl flex flex-col max-h-screen overflow-hidden">

      <!-- Header -->
      <div class="px-5 py-3 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
        <div>
          <h2 class="text-base font-semibold text-gray-900">Editar template</h2>
          <p class="text-xs text-gray-500">Personalize a aparência da página pública do formulário</p>
        </div>
        <button onclick={onCancel} class="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-400 hover:text-gray-700 cursor-pointer transition-colors" aria-label="Fechar">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <!-- Body: controles + preview -->
      <div class="flex-1 flex flex-col md:flex-row overflow-hidden">

        <!-- COLUNA ESQUERDA — CONTROLES -->
        <aside class="w-full md:w-[360px] flex-shrink-0 border-r border-gray-200 overflow-y-auto bg-gray-50/50">
          <div class="p-5 space-y-5">

            <!-- Cor -->
            <div>
              <label class="block text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">Cor do formulário</label>
              <div class="grid grid-cols-4 gap-2">
                {#each themeColors as tc}
                  <button
                    type="button"
                    onclick={() => (localTheme = tc.id)}
                    class="flex flex-col items-center gap-1.5 p-2.5 rounded-xl border-2 transition-all cursor-pointer bg-white {localTheme === tc.id ? 'border-gray-900 shadow-sm' : 'border-transparent hover:border-gray-200'}"
                  >
                    <div class="w-7 h-7 rounded-full shadow-sm" style="background: {tc.color};"></div>
                    <span class="text-[10px] font-medium text-gray-600">{tc.label}</span>
                  </button>
                {/each}
              </div>
            </div>

            <!-- Template -->
            <div>
              <label for="tpl-select" class="block text-xs font-semibold text-gray-700 uppercase tracking-wide mb-1">Template da página</label>
              <p class="text-[11px] text-gray-400 mb-2">Layout que o lead verá ao abrir o formulário</p>
              <select
                id="tpl-select"
                value={localTemplate}
                onchange={(e) => changeTemplate((e.target as HTMLSelectElement).value as PageTemplate)}
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
              >
                {#each PAGE_TEMPLATE_OPTIONS as opt}
                  <option value={opt.value}>{opt.label}</option>
                {/each}
              </select>
            </div>

            <!-- Subtítulo do card (sempre visível, em qualquer template) -->
            <div>
              <label for="tpl-card-subtitle" class="block text-xs font-semibold text-gray-700 uppercase tracking-wide mb-1">Subtítulo do formulário</label>
              <p class="text-[11px] text-gray-400 mb-2">Frase abaixo do logo no card do formulário</p>
              <input
                id="tpl-card-subtitle"
                type="text"
                value={resolvedPreview.cardSubtitle}
                oninput={(e) => updatePageField('cardSubtitle', (e.target as HTMLInputElement).value)}
                class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400"
                placeholder="Preencha seus dados para falar com nosso consultor"
              />
            </div>

            {#if localTemplate !== 'centered'}
              <div class="border border-violet-100 bg-violet-50/40 rounded-xl p-3 space-y-3">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold text-violet-700 uppercase tracking-wide">Conteúdo da página</span>
                  <button
                    type="button"
                    onclick={restorePresetDefaults}
                    class="text-[11px] text-violet-600 hover:text-violet-800 underline cursor-pointer"
                  >
                    Restaurar padrão
                  </button>
                </div>

                <div>
                  <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="tpl-banner">Barra do topo</label>
                  <input
                    id="tpl-banner"
                    type="text"
                    value={resolvedPreview.topBannerText}
                    oninput={(e) => updatePageField('topBannerText', (e.target as HTMLInputElement).value)}
                    class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400"
                  />
                </div>

                <div>
                  <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="tpl-headline">Headline</label>
                  <textarea
                    id="tpl-headline"
                    value={resolvedPreview.headline}
                    oninput={(e) => updatePageField('headline', (e.target as HTMLTextAreaElement).value)}
                    class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400 h-16 resize-y"
                  ></textarea>
                </div>

                <div>
                  <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="tpl-highlight">Destaque na headline</label>
                  <input
                    id="tpl-highlight"
                    type="text"
                    value={resolvedPreview.headlineHighlight}
                    oninput={(e) => updatePageField('headlineHighlight', (e.target as HTMLInputElement).value)}
                    class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400"
                    placeholder="Trecho da headline que recebe cor"
                  />
                </div>

                <div>
                  <span class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1">Bullets (4 itens com check)</span>
                  <div class="space-y-1.5">
                    {#each Array(4) as _, i}
                      <input
                        type="text"
                        value={resolvedPreview.bullets[i] || ''}
                        oninput={(e) => updateBullet(i, (e.target as HTMLInputElement).value)}
                        class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400"
                        placeholder={`Bullet ${i + 1}`}
                      />
                    {/each}
                  </div>
                </div>

                <div>
                  <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="tpl-disc-title">Título disciplinas</label>
                  <input
                    id="tpl-disc-title"
                    type="text"
                    value={resolvedPreview.disciplinesTitle}
                    oninput={(e) => updatePageField('disciplinesTitle', (e.target as HTMLInputElement).value)}
                    class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400"
                  />
                </div>

                <div>
                  <span class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1">Disciplinas (9 itens)</span>
                  <div class="grid grid-cols-1 gap-1.5">
                    {#each Array(9) as _, i}
                      <input
                        type="text"
                        value={resolvedPreview.disciplines[i] || ''}
                        oninput={(e) => updateDiscipline(i, (e.target as HTMLInputElement).value)}
                        class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400"
                        placeholder={`Disciplina ${i + 1}`}
                      />
                    {/each}
                  </div>
                </div>
              </div>
            {/if}
          </div>
        </aside>

        <!-- COLUNA DIREITA — PREVIEW -->
        <main class="flex-1 overflow-y-auto bg-gray-100">
          <div class="px-4 py-3 border-b border-gray-200 bg-white flex items-center gap-2 sticky top-0 z-10">
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span class="text-xs font-medium text-gray-600 uppercase tracking-wide">Preview em tempo real</span>
          </div>

          {#if localTemplate === 'centered'}
            <!-- Preview: layout centralizado em fundo preto -->
            <div class="min-h-full flex items-start justify-center p-6" style="background: #000000;">
              <div class="max-w-[460px] w-full">
                {@render previewCard()}
              </div>
            </div>
          {:else}
            <!-- Preview: layout Pós (barra topo + 2 colunas) -->
            <div class="min-h-full" style="background-color: #0d0a1f; background-image: url('{previewBgUrl}'); background-size: cover; background-position: center; background-repeat: no-repeat;">
              {#if resolvedPreview.topBannerText}
                <div class="text-white text-center text-[11px] font-bold py-2.5 px-4 tracking-wide" style="background: linear-gradient(90deg, #b91c1c 0%, #dc2626 50%, #b91c1c 100%);">
                  {resolvedPreview.topBannerText}
                </div>
              {/if}
              <div class="px-4 py-6 lg:py-10">
                <div class="grid gap-6 lg:gap-10 max-w-6xl mx-auto lg:grid-cols-[1fr_360px]">
                  <div class="lg:row-start-1 lg:col-start-1">
                    <FormPosSidebarTop content={resolvedPreview} themeMain={currentTheme.main} />
                  </div>
                  <div class="w-full max-w-[360px] mx-auto lg:mx-0 lg:justify-self-end lg:row-start-1 lg:row-span-2 lg:col-start-2 lg:self-center">
                    {@render previewCard()}
                  </div>
                  <div class="lg:row-start-2 lg:col-start-1">
                    <FormPosSidebarBottom content={resolvedPreview} themeMain={currentTheme.main} />
                  </div>
                </div>
              </div>
            </div>
          {/if}
        </main>
      </div>

      <!-- Footer: ações -->
      <div class="px-5 py-3 border-t border-gray-200 flex items-center justify-end gap-2 flex-shrink-0 bg-white">
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
          class="px-4 py-2 text-sm font-semibold text-white rounded-lg cursor-pointer transition-all active:scale-[0.98]"
          style="background: {currentTheme.gradient};"
        >
          Salvar alterações
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Snippet do card branco — usado nos dois layouts de preview -->
{#snippet previewCard()}
  <div class="bg-white/95 backdrop-blur-sm rounded-2xl border border-white/50 shadow-[0_20px_60px_rgba(15,10,26,0.35)] overflow-hidden">
    <div class="px-6 pt-2 pb-1 text-center" style="background: {currentTheme.gradientHeader};">
      <img src="https://br.itvalleyschool.com/wp-content/uploads/2024/06/logo_horizontal_mono_branca_1-1024x511.webp" alt="IT Valley School" class="h-16 mx-auto mb-1" />
      <p class="text-[12px] text-white/85 font-light">{resolvedPreview.cardSubtitle}</p>
    </div>
    <div class="px-5 py-5 space-y-3">
      <div>
        <span class="block text-[10px] font-semibold text-gray-500 mb-1 uppercase tracking-wide">Nome completo</span>
        <div class="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-400">Seu nome completo</div>
      </div>
      <div>
        <span class="block text-[10px] font-semibold text-gray-500 mb-1 uppercase tracking-wide">E-mail</span>
        <div class="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-400">seu@email.com</div>
      </div>
      <div>
        <span class="block text-[10px] font-semibold text-gray-500 mb-1 uppercase tracking-wide">WhatsApp</span>
        <div class="w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-400 mb-1.5 flex items-center gap-2">
          <span>🇧🇷</span><span>Brasil (+55)</span>
        </div>
        <div class="flex gap-1.5">
          <div class="border border-gray-200 bg-gray-50 rounded-lg px-2 py-2 text-xs text-gray-400 min-w-[80px]">DDD</div>
          <div class="flex-1 border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-400">99999-9999</div>
        </div>
      </div>
      <button
        type="button"
        disabled
        class="w-full py-2.5 rounded-lg text-sm font-semibold text-white opacity-95 cursor-default"
        style="background: {currentTheme.gradient};"
      >
        Começar
      </button>
      <p class="text-center text-[10px] text-gray-400">Powered by IT Valley School</p>
    </div>
  </div>
{/snippet}
