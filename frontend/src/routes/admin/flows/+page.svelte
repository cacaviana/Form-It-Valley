<script lang="ts">
  import { goto } from '$app/navigation';
  import { FlowsService } from '$lib/services/flows.service';
  import { authFetch } from '$lib/utils/auth-fetch';
  import type { Flow } from '$lib/dto/flows/types';
  import { onMount } from 'svelte';

  const service = new FlowsService();
  let flows = $state<Flow[]>([]);
  let loading = $state(true);

  onMount(async () => {
    flows = await service.list();
    loading = false;
  });

  function createNew() {
    goto('/admin/flows/new/edit');
  }

  async function deleteFlow(flow: Flow) {
    if (!confirm(`Excluir "${flow.name}"?`)) return;
    await authFetch(`/api/flows/${flow._id}`, { method: 'DELETE' });
    flows = flows.filter(f => f._id !== flow._id);
  }

  const statusColors: Record<string, string> = {
    draft: 'bg-yellow-100 text-yellow-800',
    published: 'bg-green-100 text-green-800',
    archived: 'bg-gray-100 text-gray-600'
  };
  const statusLabels: Record<string, string> = {
    draft: 'Rascunho',
    published: 'Publicado',
    archived: 'Arquivado'
  };
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex justify-between items-center">
    <div class="flex items-center gap-3">
      <button onclick={() => goto('/admin')} class="text-gray-400 hover:text-gray-700 cursor-pointer transition-colors p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
        </svg>
      </button>
      <div class="h-5 w-px bg-gray-200"></div>
      <h1 class="text-xl font-bold text-gray-900">Fluxos</h1>
    </div>
    <button
      onclick={createNew}
      class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 cursor-pointer"
    >
      + Novo Fluxo
    </button>
  </header>

  <main class="max-w-5xl mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Carregando...</div>
    {:else if flows.length === 0}
      <div class="text-center py-12 bg-white rounded-xl border">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6z" />
        </svg>
        <p class="text-gray-500 mb-3">Nenhum fluxo criado</p>
        <button onclick={createNew} class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 cursor-pointer">
          Criar primeiro fluxo
        </button>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each flows as flow}
          <div class="bg-white rounded-xl border hover:shadow-md transition-shadow">
            <button onclick={() => goto(`/admin/flows/${flow._id}/edit`)} class="w-full text-left p-5 pb-3 cursor-pointer">
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-gray-900 text-sm">{flow.name}</h3>
                <span class="text-xs px-2 py-0.5 rounded-full {statusColors[flow.status]}">{statusLabels[flow.status] || flow.status}</span>
              </div>
              <p class="text-xs text-gray-500">/q/{flow.slug}</p>
            </button>
            <div class="border-t px-5 py-3 flex gap-2">
              <button onclick={() => goto(`/admin/flows/${flow._id}/edit`)} class="flex-1 text-xs font-medium text-gray-600 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 rounded-md py-2 cursor-pointer transition-colors text-center">Editar</button>
              <a href="/q/{flow.slug}" target="_blank" class="flex-1 text-xs font-medium text-gray-600 hover:text-green-600 bg-gray-50 hover:bg-green-50 rounded-md py-2 cursor-pointer transition-colors text-center">Link</a>
              <button onclick={() => deleteFlow(flow)} class="text-xs font-medium text-gray-400 hover:text-red-600 bg-gray-50 hover:bg-red-50 rounded-md py-2 px-3 cursor-pointer transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </main>
</div>
