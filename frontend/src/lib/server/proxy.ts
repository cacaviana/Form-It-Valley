const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';

export function backendUrl(path: string): string {
	return `${BACKEND_URL}${path}`;
}

export function getToken(request: Request): string {
	return (request.headers.get('authorization') || '').replace('Bearer ', '');
}

export function authHeaders(request: Request): Record<string, string> {
	const token = getToken(request);
	const headers: Record<string, string> = { 'Content-Type': 'application/json' };
	if (token) headers['Authorization'] = `Bearer ${token}`;
	return headers;
}
