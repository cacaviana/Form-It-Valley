import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request }) => {
	const res = await fetch(backendUrl('/api/whatsapp-templates'), {
		headers: authHeaders(request)
	});
	if (res.ok) return json(await res.json());
	return json([]);
};
