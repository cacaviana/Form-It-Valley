<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  let morningSlots = $state(3);
  let afternoonSlots = $state(3);
  let loading = $state(true);
  let saving = $state(false);
  let saved = $state(false);

  onMount(async () => {
    try {
      const res = await fetch('/api/scheduling-config');
      if (res.ok) {
        const data = await res.json();
        morningSlots = data.morning_slots ?? 3;
        afternoonSlots = data.afternoon_slots ?? 3;
      }
    } catch (e) { /* usa defaults */ }
    loading = false;
  });

  async function save() {
    saving = true;
    saved = false;
    await fetch('/api/scheduling-config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        morning_slots: morningSlots,
        afternoon_slots: afternoonSlots
      })
    });
    saving = false;
    saved = true;
    setTimeout(() => (saved = false), 3000);
  }

  const morningHours = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30'];
  const afternoonHours = ['14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30'];
</script>

<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b px-6 py-4 flex items-center gap-3">
    <button onclick={() => goto('/admin')} class="text-gray-400 hover:text-gray-700 cursor-pointer transition-colors p-1">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
      </svg>
    </button>
    <div class="h-5 w-px bg-gray-200"></div>
    <h1 class="text-xl font-bold text-gray-900">Configuracoes</h1>
  </header>

  <main class="max-w-lg mx-auto p-6">
    {#if loading}
      <div class="text-center py-12 text-gray-500">Carregando...</div>
    {:else}
      <div class="bg-white rounded-xl border p-6 space-y-6">
        <div>
          <h2 class="text-base font-semibold text-gray-900 mb-1">Horarios disponiveis para agendamento</h2>
          <p class="text-sm text-gray-500">Defina o maximo de horarios que o lead vai ver por periodo. Os horarios sao escolhidos aleatoriamente dentre os disponiveis.</p>
        </div>

        <!-- Manha -->
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-5">
          <div class="flex items-center gap-2 mb-3">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
            </svg>
            <h3 class="font-semibold text-blue-900">Manha</h3>
            <span class="text-xs text-blue-500 ml-auto">09:00 - 11:30</span>
          </div>
          <label class="block text-sm text-blue-800 mb-2">Maximo de horarios para o lead</label>
          <div class="flex items-center gap-3">
            <input
              type="range"
              min="1"
              max={morningHours.length}
              bind:value={morningSlots}
              class="flex-1 accent-blue-600"
            />
            <span class="text-2xl font-bold text-blue-700 w-8 text-center">{morningSlots}</span>
          </div>
          <p class="text-xs text-blue-600 mt-2">De ate {morningHours.length} horarios livres, o lead vera no maximo {morningSlots} (aleatorios)</p>
        </div>

        <!-- Tarde -->
        <div class="bg-orange-50 border border-orange-200 rounded-xl p-5">
          <div class="flex items-center gap-2 mb-3">
            <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
            </svg>
            <h3 class="font-semibold text-orange-900">Tarde</h3>
            <span class="text-xs text-orange-500 ml-auto">14:00 - 17:30</span>
          </div>
          <label class="block text-sm text-orange-800 mb-2">Maximo de horarios para o lead</label>
          <div class="flex items-center gap-3">
            <input
              type="range"
              min="1"
              max={afternoonHours.length}
              bind:value={afternoonSlots}
              class="flex-1 accent-orange-600"
            />
            <span class="text-2xl font-bold text-orange-700 w-8 text-center">{afternoonSlots}</span>
          </div>
          <p class="text-xs text-orange-600 mt-2">De ate {afternoonHours.length} horarios livres, o lead vera no maximo {afternoonSlots} (aleatorios)</p>
        </div>

        <!-- Resumo -->
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p class="text-sm text-gray-700">
            O lead vera no maximo <strong>{morningSlots + afternoonSlots} horarios</strong> por dia
            ({morningSlots} de manha + {afternoonSlots} de tarde), escolhidos aleatoriamente.
          </p>
        </div>

        <!-- Save -->
        <div class="flex items-center gap-3 pt-2">
          <button
            onclick={save}
            disabled={saving}
            class="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 cursor-pointer transition-colors"
          >
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
          {#if saved}
            <span class="text-sm text-green-600 font-medium">Salvo!</span>
          {/if}
        </div>
      </div>
    {/if}
  </main>
</div>
