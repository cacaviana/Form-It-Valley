/**
 * Fetch wrapper que adiciona o token JWT do localStorage automaticamente.
 * Usar em todas as chamadas do browser para rotas admin protegidas.
 */
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
	const token = typeof localStorage !== 'undefined' ? localStorage.getItem('access_token') : null;
	const headers = new Headers(options.headers || {});
	if (token) {
		headers.set('Authorization', `Bearer ${token}`);
	}
	const res = await fetch(url, { ...options, headers });

	// Token expirado/invalido: limpa a sessao e manda pro login.
	if (res.status === 401 && typeof window !== 'undefined') {
		localStorage.removeItem('access_token');
		localStorage.removeItem('refresh_token');
		localStorage.removeItem('user');
		if (window.location.pathname !== '/login') {
			window.location.href = '/login';
		}
	}

	return res;
}
