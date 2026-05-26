<script lang="ts">
  import type { PageContent } from '$lib/dto/flows/types';

  let { content, themeMain = '#7C3AED' } = $props<{
    content: Required<PageContent>;
    themeMain?: string;
  }>();

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

<div class="text-white space-y-5 sm:space-y-6 lg:space-y-7 text-center lg:text-left">
  <!-- Selos -->
  <div class="flex items-center justify-center lg:justify-start gap-4">
    <img src="/selo_itvalley.png" alt="Selo IT Valley" class="h-14 sm:h-16 lg:h-20" />
    <img src="/selo_mec.png" alt="Reconhecido pelo MEC" class="h-14 sm:h-16 lg:h-20" />
  </div>

  <!-- Headline -->
  {#if content.headline}
    <h1 class="text-xl sm:text-2xl lg:text-4xl font-extrabold leading-tight tracking-tight">
      {headlineParts.before}<span style="color: {themeMain};">{headlineParts.highlight}</span>{headlineParts.after}
    </h1>
  {/if}

  <!-- Bullets -->
  {#if content.bullets && content.bullets.length > 0}
    <ul class="space-y-2.5 sm:space-y-3 inline-block text-left">
      {#each content.bullets as bullet}
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
  {/if}
</div>
