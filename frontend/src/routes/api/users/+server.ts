import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';

function getToken(request: Request): string {
	const auth = request.headers.get('authorization') || '';
	return auth.replace('Bearer ', '');
}

export const GET: RequestHandler = async ({ request }) => {
	const token = getToken(request);
	const res = await fetch(`${BACKEND_URL}/api/users`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	const data = await res.json();
	return json(data, { status: res.status });
};

export const POST: RequestHandler = async ({ request }) => {
	const token = getToken(request);
	const body = await request.json();
	const res = await fetch(`${BACKEND_URL}/api/users`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(body)
	});
	const data = await res.json();
	return json(data, { status: res.status });
};
