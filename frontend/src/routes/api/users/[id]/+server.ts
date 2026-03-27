import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';

function getToken(request: Request): string {
	const auth = request.headers.get('authorization') || '';
	return auth.replace('Bearer ', '');
}

export const PUT: RequestHandler = async ({ request, params }) => {
	const token = getToken(request);
	const body = await request.json();
	const res = await fetch(`${BACKEND_URL}/api/users/${params.id}`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(body)
	});
	const data = await res.json();
	return json(data, { status: res.status });
};

export const DELETE: RequestHandler = async ({ request, params }) => {
	const token = getToken(request);
	const res = await fetch(`${BACKEND_URL}/api/users/${params.id}`, {
		method: 'DELETE',
		headers: { Authorization: `Bearer ${token}` }
	});
	if (res.status === 204) return new Response(null, { status: 204 });
	const data = await res.json();
	return json(data, { status: res.status });
};
