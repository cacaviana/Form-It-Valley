<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  interface Submission {
    id: string;
    tenant_id: string;
    flow_id: string;
    flow_slug: string;
    client_name: string;
    client_email: string;
    client_phone: string | null;
    client_address: string | null;
    answers: { node_id: string; question: string; value: string }[];
    end_node_id: string;
    end_type: string;
    quote_text: string | null;
    status: string;
    created_at: string;
  }

  let submission = $state<Submission | null>(null);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      const res = await fetch(`/api/submissions/${page.params.id}`);
      if (res.ok) {
        submission = await res.json();
      } else {
        error = 'Submission non trouvee';
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
      return d.toLocaleDateString('fr-CA', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
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
        <h1 class="text-lg font-bold text-gray-900">Détail de la demande</h1>
        <p class="text-xs text-gray-500">{submission?.client_name || '...'}</p>
      </div>
    </div>
    {#if submission}
      <button
        onclick={() => window.open(`/api/submissions/${submission?.id}/export`, '_blank')}
        class="text-sm font-medium text-gray-600 hover:text-gray-800 bg-gray-100 hover:bg-gray-200 rounded-lg px-4 py-2 cursor-pointer transition-colors flex items-center gap-1.5"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
        </svg>
        Exporter &amp; Sauvegarder
      </button>
    {/if}
  </header>

  <main class="max-w-4xl mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Chargement...</div>
    {:else if error}
      <div class="text-center py-12 text-red-600">{error}</div>
    {:else if submission}
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Coluna esquerda: dados do cliente + respostas -->
        <div class="lg:col-span-1 space-y-4">
          <!-- Cliente -->
          <div class="bg-white rounded-lg border p-5">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Client</h3>
            <div class="space-y-2 text-sm">
              <p><span class="text-gray-500">Nom:</span> <span class="font-medium text-gray-900">{submission.client_name}</span></p>
              <p><span class="text-gray-500">Email:</span> <span class="text-gray-900">{submission.client_email}</span></p>
              {#if submission.client_phone}
                <p><span class="text-gray-500">Tel:</span> <span class="text-gray-900">{submission.client_phone}</span></p>
              {/if}
              {#if submission.client_address}
                <p><span class="text-gray-500">Adresse:</span> <span class="text-gray-900">{submission.client_address}</span></p>
              {/if}
            </div>
          </div>

          <!-- Respostas -->
          <div class="bg-white rounded-lg border p-5">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Réponses ({submission.answers.length})</h3>
            <div class="space-y-2">
              {#each submission.answers as answer, i}
                <div class="text-sm">
                  <p class="text-gray-500 text-xs">{i + 1}. {answer.question}</p>
                  <p class="font-medium text-gray-900">{answer.value}</p>
                </div>
              {/each}
            </div>
          </div>

          <!-- Meta -->
          <div class="bg-white rounded-lg border p-5">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3">Info</h3>
            <div class="space-y-1 text-xs text-gray-600">
              <p><span class="text-gray-500">Flow:</span> {submission.flow_slug}</p>
              <p><span class="text-gray-500">Type:</span> {submission.end_type}</p>
              <p><span class="text-gray-500">Status:</span> {submission.status}</p>
              <p><span class="text-gray-500">Date:</span> {formatDate(submission.created_at)}</p>
              <p><span class="text-gray-500">ID:</span> <code class="text-[10px] bg-gray-100 px-1 rounded">{submission.id}</code></p>
            </div>
          </div>
        </div>

        <!-- Coluna direita: devis gerado -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg border p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wide">
                {submission.end_type === 'quote' ? 'Devis généré par IA' : 'Résultat'}
              </h3>
              {#if submission.quote_text}
                <span class="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">Généré</span>
              {/if}
            </div>
            {#if submission.quote_text}
              <div class="prose prose-sm max-w-none">
                <pre class="bg-gray-50 border border-gray-200 rounded-lg p-5 text-sm whitespace-pre-wrap font-mono text-gray-700 max-h-[600px] overflow-y-auto leading-relaxed">{submission.quote_text}</pre>
              </div>
            {:else}
              <p class="text-sm text-gray-500 italic">Aucun devis généré pour cette demande.</p>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </main>
</div>
