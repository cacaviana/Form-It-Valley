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

  let deleteTarget = $state<Flow | null>(null);
  let deleting = $state(false);

  async function confirmDelete() {
    if (!deleteTarget) return;
    deleting = true;
    try {
      const res = await authFetch(`/api/flows/${deleteTarget._id}`, { method: 'DELETE' });
      if (res.ok || res.status === 204) {
        flows = flows.filter(f => f._id !== deleteTarget!._id);
        deleteTarget = null;
      } else {
        alert('Nao foi possivel excluir o fluxo.');
      }
    } catch (e) {
      alert('Erro ao excluir o fluxo.');
    } finally {
      deleting = false;
    }
  }

  let duplicateTarget = $state<Flow | null>(null);
  let newName = $state('');
  let duplicating = $state(false);

  function openDuplicate(flow: Flow) {
    duplicateTarget = flow;
    newName = `${flow.name} (cópia)`;
  }

  async function confirmDuplicate() {
    const name = newName.trim();
    if (!duplicateTarget || !name) return;
    duplicating = true;
    try {
      const created = await service.duplicate(duplicateTarget._id, name);
      flows = [created, ...flows];
      duplicateTarget = null;
    } catch (e) {
      alert('Nao foi possivel duplicar o fluxo.');
    } finally {
      duplicating = false;
    }
  }

  const statusColors: Record<string, string> = {
    draft: 'bg-yellow-100 text-yellow-800',
    published: 'bg-green-100 text-green-800',
    archived: 'bg-gray-100 text-gray-600'
  };
  const statusLabels: Record<string, string> = {
    draft: '',
    published: 'Publicado',
    archived: 'Arquivado'
  };
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex justify-between items-center">
    <div class="flex items-center gap-3">
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
                {#if flow.status !== 'draft'}
                  <span class="text-xs px-2 py-0.5 rounded-full {statusColors[flow.status]}">{statusLabels[flow.status] || flow.status}</span>
                {/if}
              </div>
              <p class="text-xs text-gray-500">/q/{flow.slug}</p>
            </button>
            <div class="border-t px-5 py-3 flex gap-2">
              <button onclick={() => goto(`/admin/flows/${flow._id}/edit`)} class="flex-1 text-xs font-medium text-gray-600 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 rounded-md py-2 cursor-pointer transition-colors text-center">Editar</button>
              <button onclick={() => goto(`/admin/flows/${flow._id}/submissions`)} class="flex-1 text-xs font-medium text-gray-600 hover:text-purple-600 bg-gray-50 hover:bg-purple-50 rounded-md py-2 cursor-pointer transition-colors text-center">Respostas</button>
              <a href="/q/{flow.slug}" target="_blank" class="flex-1 text-xs font-medium text-gray-600 hover:text-green-600 bg-gray-50 hover:bg-green-50 rounded-md py-2 cursor-pointer transition-colors text-center">Link</a>
              <button onclick={() => openDuplicate(flow)} title="Duplicar fluxo" aria-label="Duplicar fluxo" class="text-xs font-medium text-gray-400 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 rounded-md py-2 px-3 cursor-pointer transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 011.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 00-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 01-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5a3.375 3.375 0 00-3.375-3.375H9.75" /></svg>
              </button>
              <button onclick={() => deleteTarget = flow} title="Excluir fluxo" aria-label="Excluir fluxo" class="text-xs font-medium text-gray-400 hover:text-red-600 bg-gray-50 hover:bg-red-50 rounded-md py-2 px-3 cursor-pointer transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </main>
</div>

<!-- Modal: duplicar fluxo -->
{#if duplicateTarget}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    onclick={() => { if (!duplicating) duplicateTarget = null; }}
    role="presentation"
  >
    <div
      class="bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden"
      onclick={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
    >
      <div class="px-6 pt-6 pb-4">
        <h3 class="text-base font-bold text-gray-900">Duplicar fluxo</h3>
        <p class="text-sm text-gray-500 mt-1">Uma cópia de <span class="font-medium text-gray-700">{duplicateTarget.name}</span> será criada como rascunho.</p>
        <label for="dup-name" class="block text-xs font-medium text-gray-600 mt-4 mb-1.5">Nome do novo fluxo</label>
        <!-- svelte-ignore a11y_autofocus -->
        <input
          id="dup-name"
          bind:value={newName}
          onkeydown={(e) => { if (e.key === 'Enter') confirmDuplicate(); }}
          autofocus
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Ex: Pós-graduação IA ML-BG"
        />
      </div>
      <div class="px-6 pb-6 flex gap-3">
        <button
          onclick={() => { if (!duplicating) duplicateTarget = null; }}
          disabled={duplicating}
          class="flex-1 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg px-4 py-2.5 cursor-pointer transition-colors disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          onclick={confirmDuplicate}
          disabled={duplicating || !newName.trim()}
          class="flex-1 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg px-4 py-2.5 cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {duplicating ? 'Duplicando...' : 'Duplicar'}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Modal: excluir fluxo -->
{#if deleteTarget}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    onclick={() => { if (!deleting) deleteTarget = null; }}
    role="presentation"
  >
    <div
      class="bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden"
      onclick={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
    >
      <div class="px-6 pt-6 pb-4 text-center">
        <div class="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
        </div>
        <h3 class="text-base font-bold text-gray-900">Excluir fluxo</h3>
        <p class="text-sm text-gray-500 mt-1">
          Deseja realmente excluir <span class="font-medium text-gray-700">{deleteTarget.name}</span>?
        </p>
      </div>
      <div class="px-6 pb-6 flex gap-3">
        <button
          onclick={() => { if (!deleting) deleteTarget = null; }}
          disabled={deleting}
          class="flex-1 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg px-4 py-2.5 cursor-pointer transition-colors disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          onclick={confirmDelete}
          disabled={deleting}
          class="flex-1 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg px-4 py-2.5 cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {deleting ? 'Excluindo...' : 'Excluir'}
        </button>
      </div>
    </div>
  </div>
{/if}
