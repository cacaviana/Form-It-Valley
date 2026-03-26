<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  interface SchedulingFlow {
    _id: string;
    name: string;
    slug: string;
    status: string;
    node_count: number;
    version: number;
    created_at: string;
  }

  interface Scheduling {
    id: string;
    lead_name: string;
    lead_email: string;
    lead_phone: string;
    scheduled_date: string;
    scheduled_time: string;
    status: string;
    flow_slug: string;
    created_at: string;
  }

  let flows = $state<SchedulingFlow[]>([]);
  let schedulings = $state<Scheduling[]>([]);
  let loading = $state(true);
  let tab = $state<'flows' | 'bookings'>('flows');

  onMount(async () => {
    const [flowsRes, schedulingsRes] = await Promise.all([
      fetch('/api/flows?flow_type=scheduling'),
      fetch('/api/scheduling')
    ]);

    if (flowsRes.ok) flows = await flowsRes.json();
    if (schedulingsRes.ok) schedulings = await schedulingsRes.json();
    loading = false;
  });

  async function createNew() {
    const res = await fetch('/api/flows', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'Nouveau rendez-vous',
        slug: `agendamento-${Date.now()}`,
        status: 'draft',
        flow_type: 'scheduling',
        nodes: [
          { id: 'start-1', type: 'start', position: { x: 250, y: 0 }, data: { label: 'Début' } },
          { id: 'end-schedule', type: 'end', position: { x: 250, y: 200 }, data: { label: 'Planifier', endType: 'scheduling', message: 'Choisissez le meilleur jour et heure.' } },
        ],
        edges: [
          { id: 'e-start-end', source: 'start-1', target: 'end-schedule' },
        ]
      })
    });
    if (res.ok) {
      const created = await res.json();
      goto(`/admin/flows/${created._id}/edit`);
    }
  }

  async function deleteFlow(flow: SchedulingFlow) {
    if (!confirm(`Supprimer "${flow.name}" ?`)) return;
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

  const bookingStatusColors: Record<string, string> = {
    confirmed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    completed: 'bg-blue-100 text-blue-800'
  };

  function formatDate(dateStr: string): string {
    if (!dateStr) return '-';
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString('fr-CA', { day: '2-digit', month: 'short', year: 'numeric' });
  }
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex justify-between items-center">
    <div class="flex items-center gap-3">
      <button onclick={() => goto('/')} class="text-gray-400 hover:text-gray-700 cursor-pointer transition-colors p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
        </svg>
      </button>
      <div class="h-5 w-px bg-gray-200"></div>
      <div>
        <h1 class="text-xl font-bold text-gray-900">Rendez-vous</h1>
        <p class="text-sm text-gray-500">Flux de rendez-vous et réservations</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <button
        onclick={() => goto('/admin/training/scheduling')}
        class="text-sm font-medium text-amber-700 hover:text-amber-800 bg-amber-50 hover:bg-amber-100 rounded-lg px-4 py-2 cursor-pointer transition-colors flex items-center gap-1.5"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 00-.491 6.347A48.62 48.62 0 0112 20.904a48.62 48.62 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.636 50.636 0 00-2.658-.813A59.906 59.906 0 0112 3.493a59.903 59.903 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
        </svg>
        Formation
      </button>
      <button
        onclick={() => goto('/admin/flows')}
        class="text-sm font-medium text-gray-600 hover:text-blue-600 bg-gray-100 hover:bg-blue-50 rounded-lg px-4 py-2 cursor-pointer transition-colors"
      >
        Devis
      </button>
      <button
        onclick={createNew}
        class="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 cursor-pointer flex items-center gap-1.5"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
        </svg>
        + Nouveau rendez-vous
      </button>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-6">
    <!-- Tabs -->
    <div class="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
      <button
        onclick={() => tab = 'flows'}
        class="px-4 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer
        {tab === 'flows' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}"
      >
        Flux ({flows.length})
      </button>
      <button
        onclick={() => tab = 'bookings'}
        class="px-4 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer
        {tab === 'bookings' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}"
      >
        Réservations ({schedulings.length})
      </button>
    </div>

    {#if loading}
      <div class="text-center py-12 text-gray-500">Chargement...</div>

    {:else if tab === 'flows'}
      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-lg border p-4">
          <p class="text-2xl font-bold text-gray-900">{flows.length}</p>
          <p class="text-xs text-gray-500">Total de flux</p>
        </div>
        <div class="bg-white rounded-lg border p-4">
          <p class="text-2xl font-bold text-green-600">{flows.filter(f => f.status === 'published').length}</p>
          <p class="text-xs text-gray-500">Publiés</p>
        </div>
        <div class="bg-white rounded-lg border p-4">
          <p class="text-2xl font-bold text-blue-600">{schedulings.length}</p>
          <p class="text-xs text-gray-500">Total réservations</p>
        </div>
      </div>

      {#if flows.length === 0}
        <div class="text-center py-12 bg-white rounded-lg border">
          <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
          </svg>
          <p class="text-gray-500 mb-3">Aucun flux de rendez-vous</p>
          <button onclick={createNew} class="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 cursor-pointer">
            Créer le premier flux
          </button>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each flows as flow}
            <div class="bg-white rounded-lg border hover:shadow-md transition-shadow">
              <button onclick={() => goto(`/admin/flows/${flow._id}/edit`)} class="w-full text-left p-5 pb-3 cursor-pointer">
                <div class="flex justify-between items-start mb-2">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                    </svg>
                    <h3 class="font-semibold text-gray-900">{flow.name}</h3>
                  </div>
                  <span class="text-xs px-2 py-0.5 rounded-full {statusColors[flow.status]}">{statusLabels[flow.status] || flow.status}</span>
                </div>
                <p class="text-sm text-gray-500 mb-1">/q/{flow.slug}</p>
                <div class="text-xs text-gray-400">{flow.node_count ?? 0} nœuds &middot; v{flow.version}</div>
              </button>
              <div class="border-t px-5 py-3 flex gap-2">
                <button onclick={() => goto(`/admin/flows/${flow._id}/edit`)} class="flex-1 text-xs font-medium text-gray-600 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 rounded-md py-2 cursor-pointer transition-colors text-center">Éditer</button>
                <a href="/q/{flow.slug}" target="_blank" class="flex-1 text-xs font-medium text-gray-600 hover:text-green-600 bg-gray-50 hover:bg-green-50 rounded-md py-2 cursor-pointer transition-colors text-center">Lien</a>
                <button onclick={() => deleteFlow(flow)} class="text-xs font-medium text-gray-400 hover:text-red-600 bg-gray-50 hover:bg-red-50 rounded-md py-2 px-3 cursor-pointer transition-colors">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}

    {:else if tab === 'bookings'}
      {#if schedulings.length === 0}
        <div class="text-center py-12 bg-white rounded-lg border">
          <p class="text-gray-500">Aucune réservation</p>
        </div>
      {:else}
        <div class="bg-white rounded-lg border overflow-hidden">
          <table class="w-full">
            <thead>
              <tr class="border-b bg-gray-50">
                <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Lead</th>
                <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Contact</th>
                <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Date / Heure</th>
                <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Statut</th>
                <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Flux</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              {#each schedulings as s}
                <tr class="hover:bg-gray-50 transition-colors">
                  <td class="px-5 py-3">
                    <span class="font-medium text-gray-900 text-sm">{s.lead_name}</span>
                  </td>
                  <td class="px-5 py-3">
                    <div class="text-xs text-gray-600">{s.lead_email}</div>
                    {#if s.lead_phone}<div class="text-xs text-gray-400">{s.lead_phone}</div>{/if}
                  </td>
                  <td class="px-5 py-3">
                    <span class="text-sm text-gray-900">{formatDate(s.scheduled_date)}</span>
                    <span class="text-xs text-gray-500 ml-1">{s.scheduled_time}</span>
                  </td>
                  <td class="px-5 py-3">
                    <span class="text-xs px-2 py-0.5 rounded-full {bookingStatusColors[s.status] || 'bg-gray-100 text-gray-600'}">
                      {s.status === 'confirmed' ? 'Confirmé' : s.status === 'cancelled' ? 'Annulé' : s.status}
                    </span>
                  </td>
                  <td class="px-5 py-3">
                    <span class="text-xs text-gray-400">{s.flow_slug || '-'}</span>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    {/if}
  </main>
</div>
