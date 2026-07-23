<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { tryAdoptSsoSession } from '$lib/utils/sso';

  let { children } = $props();

  let authenticated = $state(false);
  let checking = $state(true);
  let ssoDenied = $state(false);

  onMount(() => {
    let token = localStorage.getItem('access_token');
    if (!token) {
      // SSO Petra Suite: sem sessao local, tenta o cookie petra_sso do portal.
      const sso = tryAdoptSsoSession();
      if (sso === 'denied') {
        ssoDenied = true;
        checking = false;
        return;
      }
      token = sso;
    }
    if (!token) {
      goto('/login');
      return;
    }

    // Verificar se o token nao expirou
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Math.floor(Date.now() / 1000);
      if (payload.exp && payload.exp < now) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        goto('/login');
        return;
      }
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      goto('/login');
      return;
    }

    // Verificar permissao para a pagina atual
    const userRaw = localStorage.getItem('user');
    if (userRaw) {
      const user = JSON.parse(userRaw);
      const path = page.url.pathname;

      // /admin (dashboard) sempre acessivel se logado
      if (path !== '/admin') {
        const pageKey = path.split('/admin/')[1]?.split('/')[0] || '';
        if (pageKey && !user.is_super_admin && !user.permissions?.includes(pageKey)) {
          goto('/admin');
          return;
        }
      }
    }

    authenticated = true;
    checking = false;
  });
</script>

{#if checking}
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-gray-400 text-sm">Verificando acesso...</div>
  </div>
{:else if ssoDenied}
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center space-y-3">
      <p data-testid="msg-sso-negado" class="text-gray-700 text-sm font-medium">
        Seu plano não inclui o Calenda
      </p>
      <a href="/login" class="text-blue-600 text-sm underline">Entrar com outra conta</a>
    </div>
  </div>
{:else if authenticated}
  {@render children()}
{/if}
