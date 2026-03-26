import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8001';

export const GET: RequestHandler = async () => {
  const res = await fetch(`${BACKEND_URL}/api/agent/info`);
  if (!res.ok) {
    return json({ error: 'Failed to fetch agent info' }, { status: res.status });
  }
  return json(await res.json());
};
