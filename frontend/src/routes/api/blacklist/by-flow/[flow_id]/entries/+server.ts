import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request, params }) => {
  const res = await fetch(backendUrl(`/api/blacklist/by-flow/${params.flow_id}/entries`), {
    headers: authHeaders(request)
  });
  return json(await res.json(), { status: res.status });
};

export const POST: RequestHandler = async ({ request, params }) => {
  const body = await request.json();
  const res = await fetch(backendUrl(`/api/blacklist/by-flow/${params.flow_id}/entries`), {
    method: 'POST',
    headers: authHeaders(request),
    body: JSON.stringify(body)
  });
  return json(await res.json(), { status: res.status });
};

export const DELETE: RequestHandler = async ({ request, params }) => {
  const body = await request.json();
  const res = await fetch(backendUrl(`/api/blacklist/by-flow/${params.flow_id}/entries`), {
    method: 'DELETE',
    headers: authHeaders(request),
    body: JSON.stringify(body)
  });
  return json(await res.json(), { status: res.status });
};
