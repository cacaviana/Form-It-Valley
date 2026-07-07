<script lang="ts">
  import { Handle, Position } from '@xyflow/svelte';
  import type { FlowNodeData } from '$lib/dto/flows/types';

  let { data } = $props<{ data: FlowNodeData }>();
</script>

<div class="node-card border-indigo-400 bg-indigo-50">
  <Handle type="target" position={Position.Top} class="!bg-indigo-500" />

  <div class="flex items-center gap-2">
    <div class="w-7 h-7 rounded-full bg-indigo-500 flex items-center justify-center flex-shrink-0">
      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <span class="font-semibold text-indigo-900 text-sm block truncate">{data.title || 'Enviar E-mail'}</span>
      <span class="text-xs text-indigo-600 block truncate">
        {#if data.emailSubject}
          {data.emailSubject}
        {:else}
          Sem assunto configurado
        {/if}
      </span>
    </div>
  </div>

  <Handle type="source" position={Position.Bottom} class="!bg-indigo-500" />
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
