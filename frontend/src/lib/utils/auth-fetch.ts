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
	return fetch(url, { ...options, headers });
}
