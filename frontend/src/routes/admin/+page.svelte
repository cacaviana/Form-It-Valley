<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  let user = $state<{ name: string; email: string; permissions: string[]; is_super_admin?: boolean } | null>(null);

  onMount(() => {
    const raw = localStorage.getItem('user');
    if (raw) user = JSON.parse(raw);
  });

  function hasPermission(page: string): boolean {
    if (!user) return false;
    if (user.is_super_admin) return true;
    return user.permissions.includes(page);
  }

  function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    goto('/login');
  }

  const pages = [
    { key: 'scheduling', label: 'Agendamentos Realizados', desc: 'Calendario e historico de agendamentos dos leads', icon: 'calendar', href: '/admin/scheduling', color: 'blue' },
    { key: 'flows', label: 'Fluxos', desc: 'Questionarios e fluxos de qualificacao', icon: 'flow', href: '/admin/flows', color: 'purple' },
    { key: 'settings', label: 'Configuracoes', desc: 'Horarios disponiveis para agendamento', icon: 'settings', href: '/admin/settings', color: 'gray' },
    { key: 'users', label: 'Usuarios', desc: 'Gestao de usuarios e permissoes', icon: 'users', href: '/admin/users', color: 'orange' },
  ];
</script>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <div class="bg-white border-b border-gray-200">
    <div class="max-w-5xl mx-auto px-6 py-4 flex justify-between items-center">
      <div>
        <h1 class="text-lg font-bold text-gray-900">FormItValley</h1>
        <p class="text-xs text-gray-500">Ola, {user?.name || user?.email || 'Admin'}</p>
      </div>
      <button
        onclick={logout}
        class="text-sm text-gray-500 hover:text-red-600 cursor-pointer transition-colors flex items-center gap-1.5"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
        </svg>
        Sair
      </button>
    </div>
  </div>

  <!-- Cards -->
  <div class="max-w-5xl mx-auto px-6 py-8">
    <h2 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Painel</h2>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
      {#each pages as page}
        {#if hasPermission(page.key)}
          <button
            onclick={() => goto(page.href)}
            class="bg-white rounded-xl border border-gray-200 p-8 text-left hover:shadow-md hover:border-gray-300 cursor-pointer transition-all group"
          >
            <div class="flex items-start gap-4">
              <div class="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0
                {page.color === 'blue' ? 'bg-blue-100 text-blue-600' : ''}
                {page.color === 'purple' ? 'bg-purple-100 text-purple-600' : ''}
                {page.color === 'green' ? 'bg-green-100 text-green-600' : ''}
                {page.color === 'gray' ? 'bg-gray-100 text-gray-600' : ''}
                {page.color === 'orange' ? 'bg-orange-100 text-orange-600' : ''}"
              >
                {#if page.icon === 'calendar'}
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" /></svg>
                {:else if page.icon === 'flow'}
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6z" /></svg>
                {:else if page.icon === 'inbox'}
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 012.012 1.244l.256.512a2.25 2.25 0 002.013 1.244h3.218a2.25 2.25 0 002.013-1.244l.256-.512a2.25 2.25 0 012.013-1.244h3.859m-17.5 0V6.75A2.25 2.25 0 016.75 4.5h10.5a2.25 2.25 0 012.25 2.25v6.75m-17.5 0v4.5A2.25 2.25 0 006.75 20.25h10.5a2.25 2.25 0 002.25-2.25v-4.5" /></svg>
                {:else if page.icon === 'settings'}
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                {:else if page.icon === 'users'}
                  <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" /></svg>
                {/if}
              </div>
              <div>
                <h3 class="font-semibold text-gray-900 text-base group-hover:text-blue-600 transition-colors">{page.label}</h3>
                <p class="text-sm text-gray-500 mt-1">{page.desc}</p>
              </div>
            </div>
          </button>
        {/if}
      {/each}
    </div>

    {#if user && !user.is_super_admin && user.permissions.length === 0}
      <div class="bg-amber-50 border border-amber-200 rounded-xl p-6 mt-4 text-center">
        <p class="text-sm text-amber-700">Voce ainda nao tem permissoes atribuidas. Contate o administrador.</p>
      </div>
    {/if}
  </div>
</div>
