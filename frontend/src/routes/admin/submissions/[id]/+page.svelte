<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { authFetch } from '$lib/utils/auth-fetch';

  interface Submission {
    id: string;
    tenant_id: string;
    flow_id: string;
    flow_slug: string;
    client_name: string;
    client_email: string;
    client_phone: string | null;
    client_address: string | null;
    answers: { node_id: string; question: string; value: string; label?: string }[];
    end_node_id: string;
    end_type: string;
    status: string;
    created_at: string;
  }

  let submission = $state<Submission | null>(null);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      const res = await authFetch(`/api/submissions/${page.params.id}`);
      if (res.ok) {
        submission = await res.json();
      } else {
        error = 'Resposta nao encontrada';
      }
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  function formatDate(iso: string): string {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch { return iso; }
  }
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <button onclick={() => goto('/admin/submissions')} class="text-gray-400 hover:text-gray-700 cursor-pointer transition-colors p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
        </svg>
      </button>
      <div class="h-5 w-px bg-gray-200"></div>
      <div>
        <h1 class="text-lg font-bold text-gray-900">Detalhe da resposta</h1>
        <p class="text-xs text-gray-500">{submission?.client_name || '...'}</p>
      </div>
    </div>
  </header>

  <main class="max-w-3xl mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Carregando...</div>
    {:else if error}
      <div class="text-center py-12 text-red-600">{error}</div>
    {:else if submission}
      <div class="space-y-4">
        <!-- Lead -->
        <div class="bg-white rounded-lg border p-5">
          <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Lead</h3>
          <div class="space-y-2 text-sm">
            <p><span class="text-gray-500">Nome:</span> <span class="font-medium text-gray-900">{submission.client_name}</span></p>
            <p><span class="text-gray-500">Email:</span> <span class="text-gray-900">{submission.client_email}</span></p>
            {#if submission.client_phone}
              <p><span class="text-gray-500">Telefone:</span> <span class="text-gray-900">{submission.client_phone}</span></p>
            {/if}
            {#if submission.client_address}
              <p><span class="text-gray-500">Endereco:</span> <span class="text-gray-900">{submission.client_address}</span></p>
            {/if}
          </div>
        </div>

        <!-- Respostas -->
        <div class="bg-white rounded-lg border p-5">
          <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Respostas ({submission.answers.length})</h3>
          <div class="space-y-3">
            {#each submission.answers as answer, i}
              <div class="text-sm border-b border-gray-100 pb-2 last:border-0 last:pb-0">
                <p class="text-gray-500 text-xs">{i + 1}. {answer.question}</p>
                <p class="font-medium text-gray-900">{answer.label || answer.value}</p>
              </div>
            {/each}
          </div>
        </div>

        <!-- Info -->
        <div class="bg-white rounded-lg border p-5">
          <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Informacoes</h3>
          <div class="space-y-1 text-xs text-gray-600">
            <p><span class="text-gray-500">Fluxo:</span> {submission.flow_slug}</p>
            <p><span class="text-gray-500">Tipo:</span> {submission.end_type}</p>
            <p><span class="text-gray-500">Status:</span> {submission.status}</p>
            <p><span class="text-gray-500">Data:</span> {formatDate(submission.created_at)}</p>
          </div>
        </div>
      </div>
    {/if}
  </main>
</div>
