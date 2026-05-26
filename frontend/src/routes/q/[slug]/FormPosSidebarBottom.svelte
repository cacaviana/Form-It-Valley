<script lang="ts">
  import type { PageContent } from '$lib/dto/flows/types';

  let { content, themeMain = '#7C3AED' } = $props<{
    content: Required<PageContent>;
    themeMain?: string;
  }>();
</script>

<div class="text-white space-y-5 sm:space-y-6 text-center lg:text-left">
  <!-- Banner: CONHEÇA NOSSAS DISCIPLINAS -->
  {#if content.disciplinesTitle}
    <div
      class="inline-block px-4 py-2 rounded-md text-sm font-bold tracking-wide"
      style="background: {themeMain};"
    >
      {content.disciplinesTitle}
    </div>
  {/if}

  <!-- Grid de disciplinas — 1 col mobile, 2 sm, 3 desktop -->
  {#if content.disciplines && content.disciplines.length > 0}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
      {#each content.disciplines as discipline}
        {#if discipline}
          <div class="bg-black/60 border border-white/10 rounded-lg px-3 py-3 text-xs sm:text-[13px] text-white/90 text-center leading-tight min-h-[60px] flex items-center justify-center">
            {discipline}
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</div>
