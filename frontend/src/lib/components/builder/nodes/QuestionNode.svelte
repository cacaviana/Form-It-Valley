<script lang="ts">
  import { Handle, Position } from '@xyflow/svelte';
  import type { FlowNodeData } from '$lib/dto/flows/types';

  let { data } = $props<{ data: FlowNodeData }>();

  const typeLabels: Record<string, string> = {
    single_choice: 'Choix unique',
    yes_no: 'Oui/Non',
    number: 'Nombre',
    text: 'Texte',
    multiple_choice: 'Choix multiple',
    date: 'Date',
    rating: 'Évaluation',
    dropdown: 'Liste',
    photo: 'Photo'
  };

  // Show individual option handles only for choice types with few options (branching)
  // For many options (like P2 brand with 7 options), show a compact summary + single output
  const MAX_VISIBLE_OPTIONS = 5;
  let optionCount = $derived((data.options || []).length);
  let showIndividualHandles = $derived(
    (data.questionType === 'single_choice' || data.questionType === 'multiple_choice' || data.questionType === 'dropdown')
    && optionCount > 0
    && optionCount <= MAX_VISIBLE_OPTIONS
  );
  let showCompactOptions = $derived(
    (data.questionType === 'single_choice' || data.questionType === 'multiple_choice' || data.questionType === 'dropdown')
    && optionCount > MAX_VISIBLE_OPTIONS
  );
</script>

<div class="node-card border-blue-400 bg-blue-50">
  <Handle type="target" position={Position.Top} class="!bg-blue-500 !w-3 !h-3 !border-2 !border-white" />

  <div class="flex items-center gap-2 mb-1">
    <div class="w-7 h-7 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01" />
      </svg>
    </div>
    <div class="min-w-0 flex-1">
      <span class="font-semibold text-blue-900 text-sm block truncate">{data.title}</span>
      <span class="text-xs text-blue-500">{typeLabels[data.questionType || 'text']}</span>
    </div>
  </div>

  {#if data.questionType === 'yes_no'}
    <!-- Sim/Não — always 2 handles -->
    <div class="flex gap-2 mt-2 ml-9">
      <div class="handle-label bg-green-100 text-green-700">
        Oui
        <Handle type="source" position={Position.Bottom} id="yes" class="!bg-green-500 !w-2.5 !h-2.5 !border-2 !border-white" />
      </div>
      <div class="handle-label bg-red-100 text-red-700">
        Non
        <Handle type="source" position={Position.Bottom} id="no" class="!bg-red-500 !w-2.5 !h-2.5 !border-2 !border-white" />
      </div>
    </div>

  {:else if showIndividualHandles}
    <!-- Few options — show each with its own handle for branching -->
    <div class="flex flex-wrap gap-1.5 mt-2 ml-9">
      {#each data.options || [] as opt}
        <div class="handle-label bg-blue-100 text-blue-700">
          {opt.label}
          <Handle type="source" position={Position.Bottom} id={opt.id} class="!bg-blue-400 !w-2.5 !h-2.5 !border-2 !border-white" />
        </div>
      {/each}
    </div>

  {:else if showCompactOptions}
    <!-- Many options — compact summary + single handle -->
    <div class="mt-2 ml-9">
      <div class="text-xs text-blue-400">{optionCount} options : {(data.options || []).slice(0, 3).map(o => o.label).join(', ')}...</div>
    </div>
    <Handle type="source" position={Position.Bottom} class="!bg-blue-500 !w-3 !h-3 !border-2 !border-white" />

  {:else}
    <!-- Number, text, date, photo, rating — single handle -->
    <Handle type="source" position={Position.Bottom} class="!bg-blue-500 !w-3 !h-3 !border-2 !border-white" />
  {/if}
</div>

<style>
  .node-card {
    border-width: 2px;
    border-style: solid;
    border-radius: 12px;
    padding: 12px 16px;
    min-width: 210px;
    max-width: 300px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    transition: box-shadow 0.15s ease;
  }
  .node-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
  .handle-label {
    position: relative;
    font-size: 11px;
    font-weight: 500;
    padding: 2px 10px;
    border-radius: 6px;
  }
</style>
