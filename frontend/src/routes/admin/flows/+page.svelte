<script lang="ts">
  import { goto } from '$app/navigation';
  import { FlowsService } from '$lib/services/flows.service';
  import type { Flow } from '$lib/dto/flows/types';
  import { onMount } from 'svelte';

  const service = new FlowsService();
  let flows = $state<Flow[]>([]);
  let loading = $state(true);

  onMount(async () => {
    const all = await service.list();
    // Filter out scheduling flows — they have their own dashboard
    flows = all.filter(f => (f as any).flow_type !== 'scheduling');
    loading = false;
  });

  function createNew() {
    goto('/admin/flows/new/edit');
  }

  async function deleteFlow(flow: Flow) {
    if (!confirm(`Supprimer le flux "${flow.name}" ? Cette action est irréversible.`)) return;
    await fetch(`/api/flows/${flow._id}`, { method: 'DELETE' });
    flows = flows.filter(f => f._id !== flow._id);
  }

  const statusColors: Record<string, string> = {
    draft: 'bg-yellow-100 text-yellow-800',
    published: 'bg-green-100 text-green-800',
    archived: 'bg-gray-100 text-gray-600'
  };

  const statusLabels: Record<string, string> = {
    draft: 'Brouillon',
    published: 'Publié',
    archived: 'Archivé'
  };
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex justify-between items-center">
    <div class="flex items-center gap-3">
      <button onclick={() => goto('/')} class="text-gray-400 hover:text-gray-700 cursor-pointer transition-colors p-1" title="Retour à l'accueil">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
        </svg>
      </button>
      <div class="h-5 w-px bg-gray-200"></div>
      <div>
        <h1 class="text-xl font-bold text-gray-900">FlowQuote</h1>
        <p class="text-sm text-gray-500">Mes Flux</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <button
        onclick={() => goto('/admin/training/quotes')}
        class="text-sm font-medium text-amber-700 hover:text-amber-800 bg-amber-50 hover:bg-amber-100 rounded-lg px-4 py-2 cursor-pointer transition-colors flex items-center gap-1.5"
        title="Formation"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 00-.491 6.347A48.62 48.62 0 0112 20.904a48.62 48.62 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.636 50.636 0 00-2.658-.813A59.906 59.906 0 0112 3.493a59.903 59.903 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
        </svg>
        Formation
      </button>
      <button
        onclick={() => goto('/admin/scheduling')}
        class="text-sm font-medium text-gray-600 hover:text-green-600 bg-gray-100 hover:bg-green-50 rounded-lg px-4 py-2 cursor-pointer transition-colors flex items-center gap-1.5"
        title="Rendez-vous"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
        </svg>
        Rendez-vous
      </button>
      <button
        onclick={() => goto('/admin/settings')}
        class="text-sm font-medium text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-lg px-4 py-2 cursor-pointer transition-colors flex items-center gap-1.5"
        title="Paramètres IA"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 010 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 010-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        IA
      </button>
      <button
        onclick={() => goto('/admin/submissions')}
        class="text-sm font-medium text-gray-600 hover:text-purple-600 bg-gray-100 hover:bg-purple-50 rounded-lg px-4 py-2 cursor-pointer transition-colors flex items-center gap-1.5"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
        </svg>
        Demandes
      </button>
      <button
        onclick={createNew}
        class="bg-petra-mid text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-petra-dark cursor-pointer"
      >
      + Nouveau Flux
    </button>
    </div>
  </header>

  <main class="max-w-5xl mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Chargement...</div>
    {:else if flows.length === 0}
      <div class="text-center py-12">
        <p class="text-gray-500 mb-4">Aucun flux créé</p>
        <button
          onclick={createNew}
          class="bg-petra-mid text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-petra-dark cursor-pointer"
        >
          Créer le premier flux
        </button>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each flows as flow}
          <div class="bg-white rounded-lg border hover:shadow-md transition-shadow">
            <!-- Card header clicável para editar -->
            <button
              onclick={() => goto(`/admin/flows/${flow._id}/edit`)}
              class="w-full text-left p-5 pb-3 cursor-pointer"
            >
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-gray-900">{flow.name}</h3>
                <span class="text-xs px-2 py-0.5 rounded-full {statusColors[flow.status]}">
                  {statusLabels[flow.status] || flow.status}
                </span>
              </div>
              <p class="text-sm text-gray-500 mb-1">/q/{flow.slug}</p>
              <div class="text-xs text-gray-400">
                {(flow as any).node_count ?? flow.nodes?.length ?? 0} nœuds &middot; v{flow.version}
              </div>
            </button>

            <!-- Ações do card -->
            <div class="border-t px-5 py-3 flex gap-2">
              <button
                onclick={() => goto(`/admin/flows/${flow._id}/edit`)}
                class="flex-1 text-xs font-medium text-gray-600 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 rounded-md py-2 cursor-pointer transition-colors flex items-center justify-center gap-1"
                title="Éditer le flux"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z" />
                </svg>
                Éditer
              </button>
              <button
                onclick={() => goto(`/admin/flows/${flow._id}/preview`)}
                class="flex-1 text-xs font-medium text-gray-600 hover:text-purple-600 bg-gray-50 hover:bg-purple-50 rounded-md py-2 cursor-pointer transition-colors flex items-center justify-center gap-1"
                title="Visualiser questionnaire"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Aperçu
              </button>
              <a
                href="/q/{flow.slug}"
                target="_blank"
                class="flex-1 text-xs font-medium text-gray-600 hover:text-green-600 bg-gray-50 hover:bg-green-50 rounded-md py-2 cursor-pointer transition-colors flex items-center justify-center gap-1"
                title="Ouvrir le lien public"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                </svg>
                Lien
              </a>
              <button
                onclick={() => deleteFlow(flow)}
                class="text-xs font-medium text-gray-400 hover:text-red-600 bg-gray-50 hover:bg-red-50 rounded-md py-2 px-2 cursor-pointer transition-colors flex items-center justify-center"
                title="Supprimer le flux"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                </svg>
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </main>
</div>
