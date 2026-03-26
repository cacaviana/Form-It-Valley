<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  type ModelOption = { id: string; label: string };
  type AvailableModels = Record<string, ModelOption[]>;

  let provider = $state('anthropic');
  let model = $state('claude-sonnet-4-20250514');
  let availableModels = $state<AvailableModels>({});
  let loading = $state(true);
  let saving = $state(false);
  let saved = $state(false);

  onMount(async () => {
    const res = await fetch('/api/settings');
    const data = await res.json();
    provider = data.provider;
    model = data.model;
    availableModels = data.available_models ?? {};
    loading = false;
  });

  function onProviderChange(p: string) {
    provider = p;
    const models = availableModels[p] ?? [];
    if (models.length > 0) model = models[0].id;
  }

  async function save() {
    saving = true;
    saved = false;
    await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, model })
    });
    saving = false;
    saved = true;
    setTimeout(() => (saved = false), 3000);
  }

  const providerLabels: Record<string, string> = {
    anthropic: 'Anthropic (Claude)',
    openai: 'OpenAI (GPT)'
  };
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex items-center gap-3">
    <button
      onclick={() => goto('/admin/flows')}
      class="text-gray-400 hover:text-gray-700 cursor-pointer transition-colors p-1"
      title="Retour"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
      </svg>
    </button>
    <div class="h-5 w-px bg-gray-200"></div>
    <div>
      <h1 class="text-xl font-bold text-gray-900">FlowQuote</h1>
      <p class="text-sm text-gray-500">Paramètres IA</p>
    </div>
  </header>

  <main class="max-w-lg mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Chargement...</div>
    {:else}
      <div class="bg-white rounded-xl border p-6 space-y-6">
        <div>
          <h2 class="text-base font-semibold text-gray-900 mb-1">Modèle IA</h2>
          <p class="text-sm text-gray-500">Choisissez le fournisseur et le modèle utilisé pour générer les devis.</p>
        </div>

        <!-- Provider selector -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Fournisseur</label>
          <div class="grid grid-cols-2 gap-3">
            {#each Object.keys(availableModels) as p}
              <button
                onclick={() => onProviderChange(p)}
                class="relative flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all text-left
                  {provider === p
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'}"
              >
                {#if p === 'anthropic'}
                  <div class="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center shrink-0">
                    <span class="text-orange-600 font-bold text-sm">A</span>
                  </div>
                {:else}
                  <div class="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center shrink-0">
                    <span class="text-green-600 font-bold text-sm">G</span>
                  </div>
                {/if}
                <span class="text-sm font-medium text-gray-800">{providerLabels[p] ?? p}</span>
                {#if provider === p}
                  <div class="absolute top-2 right-2 w-2 h-2 rounded-full bg-blue-500"></div>
                {/if}
              </button>
            {/each}
          </div>
        </div>

        <!-- Model selector -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Modèle</label>
          <div class="space-y-2">
            {#each (availableModels[provider] ?? []) as m}
              <button
                onclick={() => (model = m.id)}
                class="w-full flex items-center justify-between p-3 rounded-lg border-2 cursor-pointer transition-all text-left
                  {model === m.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'}"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">{m.label}</div>
                  <div class="text-xs text-gray-400 font-mono mt-0.5">{m.id}</div>
                </div>
                {#if model === m.id}
                  <svg class="w-5 h-5 text-blue-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
                  </svg>
                {/if}
              </button>
            {/each}
          </div>
        </div>

        <!-- Save button -->
        <div class="flex items-center gap-3 pt-2">
          <button
            onclick={save}
            disabled={saving}
            class="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 cursor-pointer transition-colors"
          >
            {saving ? 'Enregistrement...' : 'Enregistrer'}
          </button>
          {#if saved}
            <span class="text-sm text-green-600 font-medium">Enregistré ! Le prochain devis utilisera ce modèle.</span>
          {/if}
        </div>
      </div>
    {/if}
  </main>
</div>
