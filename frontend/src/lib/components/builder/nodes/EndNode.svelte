<script lang="ts">
  import { Handle, Position } from '@xyflow/svelte';
  import type { FlowNodeData } from '$lib/dto/flows/types';

  let { data } = $props<{ data: FlowNodeData }>();

  const endLabels: Record<string, string> = {
    scheduling: 'Agendar Atendimento',
    finish: 'Finalizar'
  };
</script>

<div class="node-card border-purple-400 bg-purple-50">
  <Handle type="target" position={Position.Top} class="!bg-purple-500 !w-3 !h-3 !border-2 !border-white" />

  <div class="flex items-center gap-2">
    <div class="w-7 h-7 rounded-full bg-purple-500 flex items-center justify-center flex-shrink-0">
      {#if data.endType === 'scheduling'}
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
        </svg>
      {:else}
        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
        </svg>
      {/if}
    </div>
    <div>
      <span class="font-semibold text-purple-900 text-sm">{data.title}</span>
      <span class="text-xs text-purple-500 block">{endLabels[data.endType || 'finish']}</span>
    </div>
  </div>
</div>

<style>
  .node-card {
    border-width: 2px;
    border-style: solid;
    border-radius: 12px;
    padding: 12px 16px;
    min-width: 200px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    transition: box-shadow 0.15s ease;
  }
  .node-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
</style>
