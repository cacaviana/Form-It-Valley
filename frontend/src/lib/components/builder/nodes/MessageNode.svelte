<script lang="ts">
  import { Handle, Position } from '@xyflow/svelte';
  import type { FlowNodeData } from '$lib/dto/flows/types';

  let { data } = $props<{ data: FlowNodeData }>();
</script>

<div class="node-card {data.isSpecialist ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-gray-50'}">
  <Handle type="target" position={Position.Top} class="{data.isSpecialist ? '!bg-red-500' : '!bg-gray-500'} !w-3 !h-3 !border-2 !border-white" />

  <div class="flex items-center gap-2">
    <div class="w-7 h-7 rounded-full {data.isSpecialist ? 'bg-red-500' : 'bg-gray-500'} flex items-center justify-center flex-shrink-0">
      {#if data.isSpecialist}
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
        </svg>
      {:else}
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
        </svg>
      {/if}
    </div>
    <div class="min-w-0">
      <span class="font-semibold {data.isSpecialist ? 'text-red-900' : 'text-gray-900'} text-sm block truncate">{data.title}</span>
      {#if data.isSpecialist}
        <span class="text-xs text-red-500">Encaminha para especialista</span>
      {/if}
    </div>
  </div>

  {#if data.message}
    <p class="text-xs {data.isSpecialist ? 'text-red-600' : 'text-gray-500'} mt-1.5 ml-9 truncate">{data.message}</p>
  {/if}

  <Handle type="source" position={Position.Bottom} class="{data.isSpecialist ? '!bg-red-500' : '!bg-gray-500'} !w-3 !h-3 !border-2 !border-white" />
</div>

<style>
  .node-card {
    border-width: 2px;
    border-style: solid;
    border-radius: 12px;
    padding: 12px 16px;
    min-width: 200px;
    max-width: 260px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    transition: box-shadow 0.15s ease;
  }
  .node-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
</style>
