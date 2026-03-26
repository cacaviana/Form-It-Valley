import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const BACKEND = 'http://localhost:8001';

export const GET: RequestHandler = async () => {
  const res = await fetch(`${BACKEND}/api/settings/ai`);
  const data = await res.json();
  return json(data);
};

export const PUT: RequestHandler = async ({ request }) => {
  const body = await request.json();
  const res = await fetch(`${BACKEND}/api/settings/ai`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  return json(data);
};
