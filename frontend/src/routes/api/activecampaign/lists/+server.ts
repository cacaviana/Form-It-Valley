import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8001';

export const GET: RequestHandler = async () => {
	try {
		const res = await fetch(`${BACKEND_URL}/api/activecampaign/lists`);
		if (!res.ok) return json([]);
		const data = await res.json();
		return json(data);
	} catch (e) {
		console.error('[AC Lists] Backend fetch error:', e);
		return json([]);
	}
};
