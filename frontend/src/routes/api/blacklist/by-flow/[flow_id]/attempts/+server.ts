import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request, params }) => {
  const res = await fetch(backendUrl(`/api/blacklist/by-flow/${params.flow_id}/attempts`), {
    headers: authHeaders(request)
  });
  return json(await res.json(), { status: res.status });
};
