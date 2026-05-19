<script lang="ts">
  import { Handle, Position } from '@xyflow/svelte';
  import type { FlowNodeData } from '$lib/dto/flows/types';

  let { data } = $props<{ data: FlowNodeData }>();
</script>

<div class="node-card border-red-400 bg-red-50">
  <Handle type="target" position={Position.Top} class="!bg-red-500" />

  <div class="flex items-center gap-2">
    <div class="w-7 h-7 rounded-full bg-red-500 flex items-center justify-center flex-shrink-0">
      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <span class="font-semibold text-red-900 text-sm block truncate">{data.title || 'Lista negra'}</span>
      <span class="text-xs text-red-600 block">
        {#if (data.blacklistTotalEntries ?? 0) > 0}
          {data.blacklistTotalEntries} {data.blacklistTotalEntries === 1 ? 'entrada carregada' : 'entradas carregadas'}
        {:else}
          Nenhum CSV carregado
        {/if}
      </span>
    </div>
  </div>


  <Handle type="source" position={Position.Bottom} class="!bg-red-500" />
</div>

<style>
  .node-card {
    border-width: 2px;
    border-style: solid;
    border-radius: 12px;
    padding: 12px 16px;
    min-width: 220px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    transition: box-shadow 0.15s ease;
  }
  .node-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
</style>
