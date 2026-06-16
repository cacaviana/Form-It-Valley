<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { authFetch } from '$lib/utils/auth-fetch';

  interface SubmissionSummary {
    id: string;
    flow_id: string;
    flow_slug: string;
    client_name: string;
    client_email: string;
    client_phone: string | null;
    answers: { node_id: string; question: string; value: string; label?: string }[];
    end_type: string;
    status: string;
    created_at: string;
  }

  let submissions = $state<SubmissionSummary[]>([]);
  let flowName = $state('');
  let flowSlug = $state('');
  let loading = $state(true);
  let expandedId = $state<string | null>(null);

  const flowId = page.params.id;

  onMount(async () => {
    try {
      // Buscar flow para nome e slug
      const flowRes = await authFetch(`/api/flows/${flowId}`);
      if (flowRes.ok) {
        const flow = await flowRes.json();
        flowName = flow.name || '';
        flowSlug = flow.slug || '';
      }

      // Buscar submissions do flow
      const res = await authFetch(`/api/submissions/flow/${flowId}`);
      if (res.ok) {
        const data = await res.json();
        submissions = Array.isArray(data) ? data : data.submissions || [];
      }
    } catch (e) {
      // silently fail
    } finally {
      loading = false;
    }
  });

  function toggleExpand(id: string) {
    expandedId = expandedId === id ? null : id;
  }

  let hidingId = $state<string | null>(null);
  let confirmTarget = $state<SubmissionSummary | null>(null);

  async function hideSubmission(id: string) {
    hidingId = id;
    try {
      const res = await authFetch(`/api/submissions/${id}`, { method: 'DELETE' });
      if (res.ok || res.status === 204) {
        submissions = submissions.filter((s) => s.id !== id);
        if (expandedId === id) expandedId = null;
        confirmTarget = null;
      } else {
        alert('Nao foi possivel excluir a resposta.');
      }
    } catch (e) {
      alert('Erro ao excluir a resposta.');
    } finally {
      hidingId = null;
    }
  }

  function formatDate(iso: string): string {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch { return iso; }
  }

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
    contacted: 'bg-blue-100 text-blue-800',
    quoted: 'bg-purple-100 text-purple-800'
  };
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex justify-between items-center">
    <div class="flex items-center gap-3">
      <div>
        <h1 class="text-xl font-bold text-gray-900">Respostas</h1>
        <p class="text-sm text-gray-500">
          {flowName || 'Carregando...'}
          {#if flowSlug}
            <span class="text-gray-400">· /q/{flowSlug}</span>
          {/if}
          <span class="text-gray-400">· {submissions.length} resposta{submissions.length !== 1 ? 's' : ''}</span>
        </p>
      </div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Carregando...</div>
    {:else if submissions.length === 0}
      <div class="text-center py-12 bg-white rounded-xl border">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
        </svg>
        <p class="text-gray-500">Nenhuma resposta ainda para este fluxo.</p>
        <p class="text-sm text-gray-400 mt-1">As respostas aparecerão aqui quando os leads preencherem o formulário.</p>
      </div>
    {:else}
      <div class="space-y-3">
        {#each submissions as sub}
          <div class="bg-white rounded-lg border overflow-hidden">
            <!-- Header do card -->
            <div
              onclick={() => toggleExpand(sub.id)}
              onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleExpand(sub.id); } }}
              role="button"
              tabindex="0"
              class="w-full text-left px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors cursor-pointer"
            >
              <div class="flex items-center gap-4 min-w-0">
                <div class="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-bold shrink-0">
                  {sub.client_name?.charAt(0)?.toUpperCase() || '?'}
                </div>
                <div class="min-w-0">
                  <p class="font-medium text-gray-900 text-sm truncate">{sub.client_name}</p>
                  <p class="text-xs text-gray-500 truncate">{sub.client_email}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 shrink-0">
                <span class="text-xs px-2 py-0.5 rounded-full {endTypeColors[sub.end_type] || 'bg-gray-100 text-gray-600'}">
                  {endTypeLabels[sub.end_type] || sub.end_type}
                </span>
                <span class="text-xs px-2 py-0.5 rounded-full {statusColors[sub.status] || 'bg-gray-100 text-gray-600'}">
                  {sub.status}
                </span>
                <button
                  onclick={(e) => { e.stopPropagation(); confirmTarget = sub; }}
                  title="Excluir resposta"
                  aria-label="Excluir resposta"
                  class="text-gray-400 hover:text-red-600 hover:bg-red-50 rounded p-1 cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
                </button>
                <svg class="w-4 h-4 text-gray-400 transition-transform {expandedId === sub.id ? 'rotate-180' : ''}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                </svg>
              </div>
            </div>

            <!-- Respostas expandidas -->
            {#if expandedId === sub.id}
              <div class="border-t px-5 py-4 bg-gray-50">
                <!-- Dados do lead -->
                <div class="mb-4 flex flex-wrap gap-x-6 gap-y-1 text-xs text-gray-600">
                  {#if sub.client_phone}
                    <span><span class="text-gray-400">Tel:</span> {sub.client_phone}</span>
                  {/if}
                  <span><span class="text-gray-400">Email:</span> {sub.client_email}</span>
                </div>

                <!-- Perguntas e Respostas -->
                {#if sub.answers && sub.answers.length > 0}
                  <div class="space-y-2">
                    {#each sub.answers as answer, i}
                      <div class="bg-white rounded-md border border-gray-200 px-4 py-3">
                        <p class="text-xs text-gray-500 mb-0.5">{i + 1}. {answer.question}</p>
                        <p class="text-sm font-medium text-gray-900">{answer.label || answer.value}</p>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <p class="text-sm text-gray-400">Sem respostas registradas.</p>
                {/if}

                <!-- Link para detalhe completo -->
                <div class="mt-4 pt-3 border-t border-gray-200 flex justify-end">
                  <button
                    onclick={() => goto(`/admin/submissions/${sub.id}`)}
                    class="text-xs font-medium text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 rounded px-3 py-1.5 cursor-pointer transition-colors"
                  >
                    Ver detalhe completo
                  </button>
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </main>
</div>

<!-- Modal de confirmacao de exclusao -->
{#if confirmTarget}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    onclick={() => { if (!hidingId) confirmTarget = null; }}
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
        <h3 class="text-base font-bold text-gray-900">Excluir resposta</h3>
        <p class="text-sm text-gray-500 mt-1">
          Deseja realmente excluir a resposta de <span class="font-medium text-gray-700">{confirmTarget.client_name}</span>?
        </p>
      </div>
      <div class="px-6 pb-6 flex gap-3">
        <button
          onclick={() => { if (!hidingId) confirmTarget = null; }}
          disabled={!!hidingId}
          class="flex-1 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg px-4 py-2.5 cursor-pointer transition-colors disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          onclick={() => confirmTarget && hideSubmission(confirmTarget.id)}
          disabled={!!hidingId}
          class="flex-1 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg px-4 py-2.5 cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {hidingId ? 'Excluindo...' : 'Excluir'}
        </button>
      </div>
    </div>
  </div>
{/if}
