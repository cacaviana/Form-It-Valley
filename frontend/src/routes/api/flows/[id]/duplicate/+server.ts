import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, params }) => {
	const body = await request.json();
	const res = await fetch(backendUrl(`/api/flows/${params.id}/duplicate`), {
		method: 'POST',
		headers: authHeaders(request),
		body: JSON.stringify(body)
	});
	return json(await res.json(), { status: res.status });
};
