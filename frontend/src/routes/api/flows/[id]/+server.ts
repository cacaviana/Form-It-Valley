import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request, params }) => {
	const res = await fetch(backendUrl(`/api/flows/${params.id}`), {
		headers: authHeaders(request)
	});
	return json(await res.json(), { status: res.status });
};

export const PUT: RequestHandler = async ({ request, params }) => {
	const body = await request.json();
	const res = await fetch(backendUrl(`/api/flows/${params.id}`), {
		method: 'PUT',
		headers: authHeaders(request),
		body: JSON.stringify(body)
	});
	return json(await res.json(), { status: res.status });
};

export const DELETE: RequestHandler = async ({ request, params }) => {
	const res = await fetch(backendUrl(`/api/flows/${params.id}`), {
		method: 'DELETE',
		headers: authHeaders(request)
	});
	if (res.status === 204) return new Response(null, { status: 204 });
	return json(await res.json(), { status: res.status });
};
