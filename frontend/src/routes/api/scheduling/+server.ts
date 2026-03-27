import { json } from '@sveltejs/kit';
import { getDb } from '$lib/server/db';
import type { RequestHandler } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';

/** GET /api/scheduling?action=dates&month=3&year=2026  or  ?action=slots&date=2026-03-25 */
export const GET: RequestHandler = async ({ url }) => {
	const action = url.searchParams.get('action');

	if (action === 'dates') {
		const month = url.searchParams.get('month');
		const year = url.searchParams.get('year');
		if (!month || !year) return json({ error: 'month and year required' }, { status: 400 });

		const res = await fetch(`${BACKEND_URL}/api/public/scheduling/dates?month=${month}&year=${year}`);
		const data = await res.json();
		return json(data);
	}

	if (action === 'slots') {
		const date = url.searchParams.get('date');
		if (!date) return json({ error: 'date required' }, { status: 400 });

		const res = await fetch(`${BACKEND_URL}/api/public/scheduling/slots?date=${date}`);
		const data = await res.json();
		return json(data);
	}

	// List all (admin)
	const db = await getDb();
	const all = await db.collection('scheduling')
		.find()
		.sort({ created_at: -1 })
		.limit(200)
		.toArray();

	return json(all.map(s => ({ ...s, id: s._id.toString(), _id: undefined })));
};

/** POST /api/scheduling — Proxy para rota publica do backend */
export const POST: RequestHandler = async ({ request }) => {
	const body = await request.json();

	const res = await fetch(`${BACKEND_URL}/api/public/scheduling`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});

	const data = await res.json();
	return json(data, { status: res.status });
};
