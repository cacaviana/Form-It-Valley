<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  interface SubmissionSummary {
    id: string;
    flow_id: string;
    flow_slug: string;
    client_name: string;
    client_email: string;
    end_type: string;
    status: string;
    created_at: string;
  }

  let submissions = $state<SubmissionSummary[]>([]);
  let loading = $state(true);
  let total = $state(0);

  onMount(async () => {
    try {
      const res = await fetch('/api/submissions');
      if (res.ok) {
        const data = await res.json();
        submissions = data.submissions;
        total = data.total;
      }
    } catch (e) {
      // silently fail
    } finally {
      loading = false;
    }
  });

  const endTypeLabels: Record<string, string> = {
    scheduling: 'Agendamento',
    finish: 'Finalizado',
    specialist: 'Especialista'
  };

  const endTypeColors: Record<string, string> = {
    scheduling: 'bg-blue-100 text-blue-800',
    finish: 'bg-green-100 text-green-800',
    specialist: 'bg-red-100 text-red-800'
  };

  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-green-100 text-green-800',
    contacted: 'bg-blue-100 text-blue-800'
  };

  function formatDate(iso: string): string {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch { return iso; }
  }
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
      <div>
        <h1 class="text-xl font-bold text-gray-900">Respostas</h1>
        <p class="text-sm text-gray-500">{total} resposta{total !== 1 ? 's' : ''} no total</p>
      </div>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Carregando...</div>
    {:else if submissions.length === 0}
      <div class="text-center py-12">
        <p class="text-gray-500">Nenhuma resposta por enquanto.</p>
        <p class="text-sm text-gray-400 mt-1">As respostas aparecerao aqui quando os leads preencherem um formulario.</p>
      </div>
    {:else}
      <div class="bg-white rounded-lg border overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b text-left">
              <th class="px-4 py-3 font-medium text-gray-600">Lead</th>
              <th class="px-4 py-3 font-medium text-gray-600">Fluxo</th>
              <th class="px-4 py-3 font-medium text-gray-600">Tipo</th>
              <th class="px-4 py-3 font-medium text-gray-600">Status</th>
              <th class="px-4 py-3 font-medium text-gray-600">Data</th>
              <th class="px-4 py-3 font-medium text-gray-600">Acoes</th>
            </tr>
          </thead>
          <tbody>
            {#each submissions as sub}
              <tr class="border-b hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3">
                  <p class="font-medium text-gray-900">{sub.client_name}</p>
                  <p class="text-xs text-gray-500">{sub.client_email}</p>
                </td>
                <td class="px-4 py-3">
                  <span class="text-xs text-gray-600">{sub.flow_slug}</span>
                </td>
                <td class="px-4 py-3">
                  <span class="text-xs px-2 py-0.5 rounded-full {endTypeColors[sub.end_type] || 'bg-gray-100 text-gray-600'}">
                    {endTypeLabels[sub.end_type] || sub.end_type}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span class="text-xs px-2 py-0.5 rounded-full {statusColors[sub.status] || 'bg-gray-100 text-gray-600'}">
                    {sub.status}
                  </span>
                </td>
                <td class="px-4 py-3 text-xs text-gray-500">
                  {formatDate(sub.created_at)}
                </td>
                <td class="px-4 py-3">
                  <button
                    onclick={() => goto(`/admin/submissions/${sub.id}`)}
                    class="text-xs font-medium text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 rounded px-2.5 py-1 cursor-pointer transition-colors"
                  >
                    Ver
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </main>
</div>
