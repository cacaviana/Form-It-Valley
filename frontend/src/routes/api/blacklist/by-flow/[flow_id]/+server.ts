import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request, params }) => {
  const res = await fetch(backendUrl(`/api/blacklist/by-flow/${params.flow_id}`), {
    headers: authHeaders(request)
  });
  return json(await res.json(), { status: res.status });
};

export const DELETE: RequestHandler = async ({ request, params }) => {
  const res = await fetch(backendUrl(`/api/blacklist/by-flow/${params.flow_id}`), {
    method: 'DELETE',
    headers: authHeaders(request)
  });
  return new Response(null, { status: res.status });
};
