import { json } from '@sveltejs/kit';
import { backendUrl, authHeaders } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ request, url }) => {
	const action = url.searchParams.get('action');

	if (action === 'dates') {
		const month = url.searchParams.get('month');
		const year = url.searchParams.get('year');
		const res = await fetch(backendUrl(`/api/public/scheduling/dates?month=${month}&year=${year}`));
		return json(await res.json(), { status: res.status });
	}

	if (action === 'slots') {
		const date = url.searchParams.get('date');
		const res = await fetch(backendUrl(`/api/public/scheduling/slots?date=${date}`));
		return json(await res.json(), { status: res.status });
	}

	// Admin: list all schedulings
	const res = await fetch(backendUrl('/api/scheduling'), {
		headers: authHeaders(request)
	});
	return json(await res.json(), { status: res.status });
};

export const POST: RequestHandler = async ({ request }) => {
	const body = await request.json();
	const res = await fetch(backendUrl('/api/public/scheduling'), {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});
	return json(await res.json(), { status: res.status });
};
