import { json, type RequestHandler } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';

export const GET: RequestHandler = async ({ request, params }) => {
	const res = await fetch(backendUrl(`/api/submissions/flow/${params.flowId}`), {
		headers: authHeaders(request)
	});
	return json(await res.json(), { status: res.status });
};
