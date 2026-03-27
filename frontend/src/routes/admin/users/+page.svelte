<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  interface User {
    id: string;
    name: string;
    email: string;
    permissions: string[];
    active: boolean;
    created_at: string;
  }

  const allPages = [
    { key: 'scheduling', label: 'Agendamento' },
    { key: 'flows', label: 'Fluxos' },
    { key: 'settings', label: 'Configuracoes' },
    { key: 'users', label: 'Usuarios' },
  ];

  let users = $state<User[]>([]);
  let loading = $state(true);
  let showForm = $state(false);
  let editingUser = $state<User | null>(null);
  let saving = $state(false);
  let formError = $state('');

  // Form fields
  let formName = $state('');
  let formEmail = $state('');
  let formPassword = $state('');
  let formPasswordConfirm = $state('');
  let formPermissions = $state<string[]>([]);
  let formActive = $state(true);
  let showPassword = $state(false);
  let showPasswordConfirm = $state(false);

  function getToken(): string {
    return localStorage.getItem('access_token') || '';
  }

  async function loadUsers() {
    loading = true;
    try {
      const res = await fetch('/api/users', {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      if (res.ok) {
        const data = await res.json();
        users = data.users || [];
      }
    } catch (e) { /* silent */ }
    loading = false;
  }

  onMount(loadUsers);

  function openCreate() {
    editingUser = null;
    formName = '';
    formEmail = '@forms.com';
    formPassword = '';
    formPasswordConfirm = '';
    formPermissions = [];
    formActive = true;
    formError = '';
    showPassword = false;
    showPasswordConfirm = false;
    showForm = true;
  }

  function openEdit(user: User) {
    editingUser = user;
    formName = user.name;
    formEmail = user.email;
    formPassword = '';
    formPasswordConfirm = '';
    formPermissions = [...user.permissions];
    formActive = user.active;
    formError = '';
    showPassword = false;
    showPasswordConfirm = false;
    showForm = true;
  }

  function togglePermission(key: string) {
    if (formPermissions.includes(key)) {
      formPermissions = formPermissions.filter(p => p !== key);
    } else {
      formPermissions = [...formPermissions, key];
    }
  }

  async function handleSave() {
    formError = '';
    saving = true;

    // Validar senhas
    if (formPassword || formPasswordConfirm) {
      if (formPassword !== formPasswordConfirm) {
        formError = 'As senhas nao coincidem';
        saving = false;
        return;
      }
      if (formPassword.length < 6) {
        formError = 'A senha deve ter pelo menos 6 caracteres';
        saving = false;
        return;
      }
    }

    try {
      if (editingUser) {
        // Update
        const body: Record<string, unknown> = {
          name: formName,
          email: formEmail,
          permissions: formPermissions,
          active: formActive,
        };
        if (formPassword) body.password = formPassword;

        const res = await fetch(`/api/users/${editingUser.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
          body: JSON.stringify(body)
        });
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          formError = data.detail || 'Erro ao atualizar';
          saving = false;
          return;
        }
      } else {
        // Create
        if (!formPassword) {
          formError = 'Senha obrigatoria para novo usuario';
          saving = false;
          return;
        }
        const res = await fetch('/api/users', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
          body: JSON.stringify({
            name: formName,
            email: formEmail,
            password: formPassword,
            permissions: formPermissions,
            active: formActive
          })
        });
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          formError = data.detail || 'Erro ao criar';
          saving = false;
          return;
        }
      }

      showForm = false;
      await loadUsers();
    } catch (e) {
      formError = 'Erro de conexao';
    } finally {
      saving = false;
    }
  }

  async function handleDelete(user: User) {
    if (!confirm(`Remover ${user.name}?`)) return;
    await fetch(`/api/users/${user.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    await loadUsers();
  }
</script>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <div class="bg-white border-b border-gray-200">
    <div class="max-w-5xl mx-auto px-6 py-4 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <button onclick={() => goto('/admin')} class="text-gray-400 hover:text-gray-700 cursor-pointer">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
        </button>
        <h1 class="text-lg font-bold text-gray-900">Gestao de Usuarios</h1>
      </div>
      <button
        onclick={openCreate}
        class="bg-blue-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-blue-700 cursor-pointer transition-colors"
      >
        + Novo Usuario
      </button>
    </div>
  </div>

  <div class="max-w-5xl mx-auto px-6 py-6">
    {#if loading}
      <div class="text-center py-12 text-gray-400 text-sm">Carregando...</div>
    {:else if users.length === 0}
      <div class="text-center py-12">
        <p class="text-gray-500 text-sm">Nenhum usuario cadastrado.</p>
        <button onclick={openCreate} class="mt-3 text-blue-600 text-sm font-medium hover:underline cursor-pointer">Criar primeiro usuario</button>
      </div>
    {:else}
      <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Nome</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Email</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Permissoes</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase">Acoes</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            {#each users as user}
              <tr class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm font-medium text-gray-900">{user.name}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{user.email}</td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-1">
                    {#each user.permissions as perm}
                      <span class="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded font-medium">{perm}</span>
                    {/each}
                    {#if user.permissions.length === 0}
                      <span class="text-[10px] text-gray-400">Sem permissoes</span>
                    {/if}
                  </div>
                </td>
                <td class="px-4 py-3">
                  {#if user.active}
                    <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Ativo</span>
                  {:else}
                    <span class="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">Inativo</span>
                  {/if}
                </td>
                <td class="px-4 py-3 text-right">
                  <button onclick={() => openEdit(user)} class="text-blue-600 hover:text-blue-800 text-xs font-medium cursor-pointer mr-3">Editar</button>
                  <button onclick={() => handleDelete(user)} class="text-red-500 hover:text-red-700 text-xs font-medium cursor-pointer">Remover</button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<!-- Modal Form -->
{#if showForm}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl w-full max-w-md p-6 shadow-2xl">
      <h2 class="text-lg font-bold text-gray-900 mb-4">{editingUser ? 'Editar Usuario' : 'Novo Usuario'}</h2>

      {#if formError}
        <div class="bg-red-50 border border-red-200 rounded-lg px-3 py-2 mb-4 text-sm text-red-700">{formError}</div>
      {/if}

      <div class="space-y-3">
        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase mb-1">Nome</label>
          <input type="text" bind:value={formName} required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase mb-1">Email</label>
          <input type="email" bind:value={formEmail} required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase mb-1">
            Senha {editingUser ? '(deixe vazio para manter)' : ''}
          </label>
          <div class="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              bind:value={formPassword}
              class="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={editingUser ? '********' : ''}
            />
            <button
              type="button"
              onclick={() => showPassword = !showPassword}
              class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer p-1"
            >
              {#if showPassword}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" /></svg>
              {:else}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              {/if}
            </button>
          </div>
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase mb-1">Confirmar senha</label>
          <div class="relative">
            <input
              type={showPasswordConfirm ? 'text' : 'password'}
              bind:value={formPasswordConfirm}
              class="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500
                {formPasswordConfirm && formPassword !== formPasswordConfirm ? 'border-red-300 focus:ring-red-500' : ''}"
              placeholder={editingUser ? '********' : ''}
            />
            <button
              type="button"
              onclick={() => showPasswordConfirm = !showPasswordConfirm}
              class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer p-1"
            >
              {#if showPasswordConfirm}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" /></svg>
              {:else}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              {/if}
            </button>
          </div>
          {#if formPasswordConfirm && formPassword !== formPasswordConfirm}
            <p class="text-xs text-red-500 mt-1">As senhas nao coincidem</p>
          {/if}
        </div>

        <!-- Permissoes -->
        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase mb-2">Permissoes</label>
          <div class="space-y-2">
            {#each allPages as page}
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formPermissions.includes(page.key)}
                  onchange={() => togglePermission(page.key)}
                  class="rounded border-gray-300"
                />
                <span class="text-sm text-gray-700">{page.label}</span>
              </label>
            {/each}
          </div>
        </div>

        <!-- Ativo -->
        <label class="flex items-center gap-2 cursor-pointer pt-1">
          <input type="checkbox" bind:checked={formActive} class="rounded border-gray-300" />
          <span class="text-sm text-gray-700">Usuario ativo</span>
        </label>
      </div>

      <div class="flex gap-3 mt-6">
        <button
          onclick={() => showForm = false}
          class="flex-1 border border-gray-300 rounded-lg py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer"
        >
          Cancelar
        </button>
        <button
          onclick={handleSave}
          disabled={saving || !formName || !formEmail}
          class="flex-1 bg-blue-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 cursor-pointer"
        >
          {saving ? 'Salvando...' : 'Salvar'}
        </button>
      </div>
    </div>
  </div>
{/if}
