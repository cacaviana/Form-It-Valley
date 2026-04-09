import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request }) => {
	const res = await fetch(backendUrl('/api/submissions'), {
		headers: authHeaders(request)
	});
	return json(await res.json(), { status: res.status });
};

export const POST: RequestHandler = async ({ request }) => {
	const body = await request.json();
	const res = await fetch(backendUrl('/api/public/submissions'), {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});
	return json(await res.json(), { status: res.status });
};
