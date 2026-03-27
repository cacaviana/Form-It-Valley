import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request, url }) => {
	const params = url.searchParams.toString();
	const res = await fetch(backendUrl(`/api/flows${params ? '?' + params : ''}`), {
		headers: authHeaders(request)
	});
	return json(await res.json(), { status: res.status });
};

export const POST: RequestHandler = async ({ request }) => {
	const body = await request.json();
	const res = await fetch(backendUrl('/api/flows'), {
		method: 'POST',
		headers: authHeaders(request),
		body: JSON.stringify(body)
	});
	return json(await res.json(), { status: res.status });
};
