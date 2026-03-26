<script lang="ts">
  import type { NodeType } from '$lib/dto/flows/types';

  let { onAddNode } = $props<{ onAddNode: (type: NodeType) => void }>();

  const nodeTypes: { type: NodeType; label: string; color: string; iconPath: string }[] = [
    {
      type: 'question',
      label: 'Question',
      color: 'bg-blue-50 border-blue-300 text-blue-700 hover:bg-blue-100',
      iconPath: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01'
    },
    {
      type: 'message',
      label: 'Message',
      color: 'bg-gray-50 border-gray-300 text-gray-700 hover:bg-gray-100',
      iconPath: 'M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z'
    },
    {
      type: 'end',
      label: 'Fin',
      color: 'bg-purple-50 border-purple-300 text-purple-700 hover:bg-purple-100',
      iconPath: 'M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    }
  ];
</script>

<div class="flex items-center gap-1.5 p-2 bg-white rounded-xl shadow-sm border border-gray-200">
  <span class="text-xs font-medium text-gray-400 px-2 uppercase tracking-wider">Ajouter :</span>
  {#each nodeTypes as nt}
    <button
      class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium cursor-pointer transition-all {nt.color}"
      onclick={() => onAddNode(nt.type)}
    >
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d={nt.iconPath} />
      </svg>
      {nt.label}
    </button>
  {/each}
</div>
