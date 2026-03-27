import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request }) => {
	const res = await fetch(backendUrl('/api/scheduling-config'), {
		headers: authHeaders(request)
	});
	return json(await res.json(), { status: res.status });
};

export const PUT: RequestHandler = async ({ request }) => {
	const body = await request.json();
	const res = await fetch(backendUrl('/api/scheduling-config'), {
		method: 'PUT',
		headers: authHeaders(request),
		body: JSON.stringify(body)
	});
	return json(await res.json(), { status: res.status });
};
