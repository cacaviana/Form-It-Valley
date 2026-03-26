<script lang="ts">
  import { Handle, Position } from '@xyflow/svelte';

  let { data } = $props<{ data: { title: string } }>();
</script>

<div class="node-card border-green-400 bg-green-50">
  <div class="flex items-center gap-2">
    <div class="w-7 h-7 rounded-full bg-green-500 flex items-center justify-center">
      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
        <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
      </svg>
    </div>
    <span class="font-semibold text-green-900 text-sm">{data.title}</span>
  </div>
  <p class="text-xs text-green-600 mt-1.5 ml-9">Collecte nom, email, téléphone</p>
  <Handle type="source" position={Position.Bottom} class="!bg-green-500 !w-3 !h-3 !border-2 !border-white" />
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
