import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';

export const POST: RequestHandler = async ({ request }) => {
	const body = await request.json();

	const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});

	const data = await res.json();
	return json(data, { status: res.status });
};
