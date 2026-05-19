<script lang="ts">
  import {
    listEntries,
    uploadBlacklistCsv,
    deleteBlacklist,
    addEntry,
    removeEntry,
    type BlacklistEntry
  } from '$lib/services/blacklistService';

  let { flowId, onClose, onChange } = $props<{
    flowId: string;
    onClose: () => void;
    onChange: (total: number) => void;
  }>();

  let entries = $state<BlacklistEntry[]>([]);
  let loading = $state(true);
  let dragOver = $state(false);
  let uploading = $state(false);
  let uploadError = $state('');
  let fileInput = $state<HTMLInputElement | null>(null);

  // Mini-form pra adicionar
  let newEmail = $state('');
  let newDdi = $state('');
  let newDdd = $state('');
  let newNumero = $state('');
  let addError = $state('');
  let adding = $state(false);

  // Busca
  let query = $state('');
  let filtered = $derived(
    query.trim()
      ? entries.filter(
          (e) =>
            (e.email || '').toLowerCase().includes(query.toLowerCase()) ||
            (e.phone || '').includes(query.replace(/\D/g, ''))
        )
      : entries
  );

  const BLACKLIST_CSV_TEMPLATE = `email,ddi,ddd,numero
joao.spam@example.com,55,11,999990000
maria.bloqueada@example.com,55,21,988887777
,55,31,987654321
contato@concorrente.com.br,55,11,977778888
,1,415,5550100`;

  function downloadTemplate() {
    const blob = new Blob([BLACKLIST_CSV_TEMPLATE], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'modelo_lista_negra.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  async function refresh() {
    loading = true;
    entries = await listEntries(flowId);
    loading = false;
    onChange(entries.length);
  }

  async function handleFile(file: File) {
    uploadError = '';
    // Pré-validação UX
    const text = await file.text();
    const firstLine = text.split('\n')[0]?.trim().toLowerCase().replace(/\r$/, '');
    if (firstLine !== 'email,ddi,ddd,numero') {
      uploadError = `Cabeçalho inválido. Esperado: email,ddi,ddd,numero — Recebido: ${firstLine || '(vazio)'}`;
      return;
    }
    uploading = true;
    try {
      await uploadBlacklistCsv(flowId, file);
      await refresh();
    } catch (err) {
      uploadError = (err as Error).message;
    } finally {
      uploading = false;
    }
  }

  function formatPhone(phone: string | null): string {
    if (!phone) return '—';
    // Sempre prefixa com + na visualizacao (o backend guarda só digitos).
    // Heuristica por tamanho e prefixo conhecido.
    const d = phone.replace(/\D/g, '');
    if (d.length <= 4) return `+${d}`;

    // BR completo: 55 + DDD(2) + numero(9 = 9+4+4) = 13. Ex: +55 11 99999 0000
    if (d.length === 13 && d.startsWith('55')) {
      return `+55 ${d.slice(2, 4)} ${d.slice(4, 9)} ${d.slice(9)}`;
    }
    // US completo: 1 + AAA + NNN-NNNN = 11
    if (d.length === 11 && d.startsWith('1')) {
      return `+1 ${d.slice(1, 4)} ${d.slice(4, 7)} ${d.slice(7)}`;
    }
    // FR completo: 33 + 1 char + 8 = 11
    if (d.length === 11 && d.startsWith('33')) {
      return `+33 ${d.slice(2, 3)} ${d.slice(3, 5)} ${d.slice(5, 7)} ${d.slice(7, 9)} ${d.slice(9)}`;
    }
    // Fallback generico: separa os 4 finais e mostra o resto agrupado
    if (d.length <= 8) return `+${d.slice(0, -4)} ${d.slice(-4)}`;
    return `+${d.slice(0, -8)} ${d.slice(-8, -4)} ${d.slice(-4)}`;
  }

  const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const DIGITS_ONLY_REGEX = /^\d+$/;

  function initialFor(email: string | null, phone: string | null): string {
    if (email) return email[0].toUpperCase();
    if (phone) return '#';
    return '?';
  }

  async function onAdd() {
    addError = '';
    const email = newEmail.trim();
    const ddi = newDdi.trim();
    const ddd = newDdd.trim();
    const numero = newNumero.trim();

    if (!email && !numero) {
      addError = 'Informe pelo menos um email ou telefone';
      return;
    }
    if (email && !EMAIL_REGEX.test(email)) {
      addError = 'Email inválido (formato esperado: nome@dominio.com)';
      return;
    }
    if (ddi && !DIGITS_ONLY_REGEX.test(ddi)) {
      addError = 'DDI deve conter apenas dígitos';
      return;
    }
    if (ddd && !DIGITS_ONLY_REGEX.test(ddd)) {
      addError = 'DDD deve conter apenas dígitos';
      return;
    }
    if (numero && !DIGITS_ONLY_REGEX.test(numero)) {
      addError = 'Número deve conter apenas dígitos';
      return;
    }
    if (numero && (!ddi || !ddd)) {
      addError = 'Para telefone, preencha DDI + DDD + Número';
      return;
    }
    adding = true;
    try {
      await addEntry(flowId, {
        email: newEmail || undefined,
        ddi: newDdi || undefined,
        ddd: newDdd || undefined,
        numero: newNumero || undefined
      });
      newEmail = '';
      newDdi = '';
      newDdd = '';
      newNumero = '';
      await refresh();
    } catch (err) {
      addError = (err as Error).message;
    } finally {
      adding = false;
    }
  }

  async function onRemove(entry: BlacklistEntry) {
    if (!confirm('Remover esta entrada da lista negra?')) return;
    try {
      await removeEntry(flowId, { email: entry.email, phone: entry.phone });
      await refresh();
    } catch (err) {
      alert((err as Error).message);
    }
  }

  async function onDeleteAll() {
    if (!confirm('Remover TODA a lista negra? Esta ação é irreversível.')) return;
    try {
      await deleteBlacklist(flowId);
      await refresh();
    } catch (err) {
      alert((err as Error).message);
    }
  }

  // Carrega entries ao abrir
  $effect(() => {
    if (flowId) refresh();
  });
</script>

<div class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
  <div class="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col">
    <!-- Header -->
    <div class="px-6 py-4 border-b flex items-center justify-between">
      <div>
        <h2 class="text-base font-bold text-gray-900">Lista negra — gestão</h2>
        <p class="text-xs text-gray-500 mt-0.5">Gerencie os leads bloqueados deste formulário. Email ou telefone: um match já bloqueia.</p>
      </div>
      <button onclick={onClose} class="text-gray-400 hover:text-gray-600 cursor-pointer p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div class="p-6 overflow-y-auto flex-1 space-y-4">
      <!-- Banner do modelo -->
      <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
          </svg>
          <span class="text-sm text-amber-800">Formato esperado: <code class="bg-amber-100 px-1.5 py-0.5 rounded text-xs">email,ddi,ddd,numero</code></span>
        </div>
        <button
          onclick={downloadTemplate}
          class="text-xs font-semibold text-amber-800 bg-amber-100 hover:bg-amber-200 px-3 py-1.5 rounded-md cursor-pointer transition-colors"
        >
          Baixar modelo
        </button>
      </div>

      <!-- Drop zone -->
      <div
        class="border-2 border-dashed rounded-xl p-6 text-center transition-colors {dragOver ? 'border-red-500 bg-red-50' : 'border-gray-300 hover:border-gray-400'}"
        ondragover={(e) => { e.preventDefault(); dragOver = true; }}
        ondragleave={() => (dragOver = false)}
        ondrop={(e) => { e.preventDefault(); dragOver = false; const f = e.dataTransfer?.files[0]; if (f) handleFile(f); }}
      >
        <svg class="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
        <p class="text-sm text-gray-600 font-medium mb-1">Arraste seu CSV aqui para substituir a lista</p>
        <p class="text-xs text-gray-400 mb-3">ou</p>
        <button
          type="button"
          onclick={() => fileInput?.click()}
          disabled={uploading}
          class="inline-block bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50 cursor-pointer transition-colors"
        >
          {uploading ? 'Enviando...' : 'Escolher arquivo'}
        </button>
        <input
          bind:this={fileInput}
          type="file"
          accept=".csv,text/csv"
          class="hidden"
          onchange={(e) => { const f = (e.target as HTMLInputElement).files?.[0]; if (f) { handleFile(f); (e.target as HTMLInputElement).value = ''; } }}
        />
      </div>

      {#if uploadError}
        <div class="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
          <svg class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p class="text-sm text-red-700">{uploadError}</p>
        </div>
      {/if}

      <!-- Adicionar entry manual -->
      <div class="border border-gray-200 rounded-lg p-3">
        <h3 class="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">Adicionar entrada</h3>
        <div class="grid grid-cols-12 gap-2 items-center">
          <input
            type="email"
            placeholder="email@exemplo.com"
            bind:value={newEmail}
            class="col-span-5 input"
          />
          <input
            type="text"
            placeholder="DDI"
            bind:value={newDdi}
            class="col-span-1 input text-center"
            maxlength="3"
            inputmode="numeric"
            pattern="\d*"
            oninput={(e) => { const t = e.target as HTMLInputElement; t.value = t.value.replace(/\D/g, ''); newDdi = t.value; }}
          />
          <input
            type="text"
            placeholder="DDD"
            bind:value={newDdd}
            class="col-span-1 input text-center"
            maxlength="3"
            inputmode="numeric"
            pattern="\d*"
            oninput={(e) => { const t = e.target as HTMLInputElement; t.value = t.value.replace(/\D/g, ''); newDdd = t.value; }}
          />
          <input
            type="text"
            placeholder="999999999"
            bind:value={newNumero}
            class="col-span-3 input"
            inputmode="numeric"
            pattern="\d*"
            oninput={(e) => { const t = e.target as HTMLInputElement; t.value = t.value.replace(/\D/g, ''); newNumero = t.value; }}
          />
          <button
            type="button"
            onclick={onAdd}
            disabled={adding}
            class="col-span-2 bg-gray-900 text-white text-xs font-semibold rounded-lg py-2 hover:bg-gray-800 disabled:opacity-50 cursor-pointer"
          >
            {adding ? '...' : 'Adicionar'}
          </button>
        </div>
        {#if addError}
          <p class="text-xs text-red-600 mt-1.5">{addError}</p>
        {/if}
      </div>

      <!-- Lista atual -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-xs font-semibold text-gray-600 uppercase tracking-wide">
            Lista atual ({entries.length})
          </h3>
          {#if entries.length > 0}
            <input
              type="text"
              placeholder="Buscar..."
              bind:value={query}
              class="text-xs border border-gray-200 rounded-md px-2 py-1 w-48 focus:outline-none focus:border-gray-400"
            />
          {/if}
        </div>

        {#if loading}
          <p class="text-xs text-gray-400 py-6 text-center">Carregando...</p>
        {:else if entries.length === 0}
          <div class="border border-gray-100 rounded-lg p-6 text-center bg-gray-50/50">
            <p class="text-sm text-gray-500">Nenhuma entrada na lista negra</p>
            <p class="text-xs text-gray-400 mt-1">Importe um CSV ou adicione manualmente acima</p>
          </div>
        {:else}
          <div class="border border-gray-200 rounded-lg overflow-hidden">
            <div class="max-h-72 overflow-y-auto">
              <table class="w-full text-sm">
                <thead class="bg-gray-50 sticky top-0">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase w-12"></th>
                    <th class="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Email</th>
                    <th class="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Telefone</th>
                    <th class="px-3 py-2 w-10"></th>
                  </tr>
                </thead>
                <tbody>
                  {#each filtered as entry, i}
                    <tr class="group border-t border-gray-100 hover:bg-red-50/30">
                      <td class="px-3 py-2">
                        <div class="w-7 h-7 rounded-full bg-gray-200 text-gray-600 text-xs font-semibold flex items-center justify-center">
                          {initialFor(entry.email, entry.phone)}
                        </div>
                      </td>
                      <td class="px-3 py-2 text-gray-700 text-sm truncate max-w-[220px]">
                        {entry.email || '—'}
                      </td>
                      <td class="px-3 py-2 text-gray-600 text-sm font-mono">
                        {formatPhone(entry.phone)}
                      </td>
                      <td class="px-3 py-2 text-right">
                        <button
                          type="button"
                          onclick={() => onRemove(entry)}
                          class="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-600 cursor-pointer"
                          title="Remover esta entrada"
                          aria-label="Remover"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </div>
          {#if filtered.length === 0 && query}
            <p class="text-xs text-gray-400 mt-2 text-center">Nenhum resultado para "{query}"</p>
          {/if}
        {/if}
      </div>
    </div>

    <!-- Footer -->
    <div class="px-6 py-3 border-t flex justify-between items-center">
      {#if entries.length > 0}
        <button
          onclick={onDeleteAll}
          class="text-xs text-red-600 px-3 py-2 rounded-lg hover:bg-red-50 cursor-pointer transition-colors font-medium"
        >
          Excluir lista inteira
        </button>
      {:else}
        <span></span>
      {/if}
      <button
        onclick={onClose}
        class="text-sm font-medium text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
      >
        Fechar
      </button>
    </div>
  </div>
</div>

<style>
  .input {
    width: 100%;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
    outline: none;
    background: white;
  }
  .input:focus {
    border-color: #9ca3af;
    box-shadow: 0 0 0 3px rgba(156, 163, 175, 0.15);
  }
</style>
