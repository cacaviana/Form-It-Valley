<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  onMount(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      goto('/admin');
    } else {
      goto('/login');
    }
  });
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50">
  <div class="text-gray-400 text-sm">Redirecionando...</div>
</div>
