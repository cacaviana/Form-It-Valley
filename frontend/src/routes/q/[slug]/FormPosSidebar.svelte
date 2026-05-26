<script lang="ts">
  import type { PageContent } from '$lib/dto/flows/types';

  let { content, themeMain = '#7C3AED' } = $props<{
    content: Required<PageContent>;
    themeMain?: string;
  }>();

  // Quebra a headline em 3 partes: antes do destaque, destaque, depois
  let headlineParts = $derived.by(() => {
    const text = content.headline || '';
    const hl = content.headlineHighlight || '';
    if (!hl) return { before: text, highlight: '', after: '' };
    const idx = text.toLowerCase().indexOf(hl.toLowerCase());
    if (idx === -1) return { before: text, highlight: '', after: '' };
    return {
      before: text.slice(0, idx),
      highlight: text.slice(idx, idx + hl.length),
      after: text.slice(idx + hl.length)
    };
  });
</script>

<aside class="text-white space-y-6 lg:space-y-8">
  <!-- Logos -->
  <div class="flex items-center gap-4">
    <img
      src="/selo_itvalley.png"
      alt="Selo IT Valley"
      class="h-16 sm:h-20"
    />
    <img
      src="/selo_mec.png"
      alt="Reconhecido pelo MEC"
      class="h-16 sm:h-20"
    />
  </div>

  <!-- Headline -->
  <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold leading-tight tracking-tight">
    {headlineParts.before}<span style="color: {themeMain};">{headlineParts.highlight}</span>{headlineParts.after}
  </h1>

  <!-- Bullets -->
  <ul class="space-y-3">
    {#each content.bullets || [] as bullet}
      {#if bullet}
        <li class="flex items-start gap-3 text-sm sm:text-base text-white/90">
          <span class="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center mt-0.5">
            <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </span>
          <span>{bullet}</span>
        </li>
      {/if}
    {/each}
  </ul>

  <!-- Banner: CONHEÇA NOSSAS DISCIPLINAS -->
  {#if content.disciplinesTitle}
    <div
      class="inline-block px-4 py-2 rounded-md text-sm font-bold tracking-wide"
      style="background: {themeMain};"
    >
      {content.disciplinesTitle}
    </div>
  {/if}

  <!-- Grid 3x3 de disciplinas -->
  {#if content.disciplines && content.disciplines.length > 0}
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
      {#each content.disciplines as discipline}
        {#if discipline}
          <div class="bg-black/60 border border-white/10 rounded-lg px-3 py-3 text-xs sm:text-[13px] text-white/90 text-center leading-tight min-h-[60px] flex items-center justify-center">
            {discipline}
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</aside>
