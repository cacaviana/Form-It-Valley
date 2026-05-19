import { backendUrl, getToken } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
  // Multipart: NAO setar Content-Type — o fetch define com boundary automaticamente
  const body = await request.formData();
  const token = getToken(request);
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(backendUrl('/api/blacklist/upload'), {
    method: 'POST',
    headers,
    body
  });
  const text = await res.text();
  return new Response(text, {
    status: res.status,
    headers: { 'Content-Type': res.headers.get('content-type') || 'application/json' }
  });
};
