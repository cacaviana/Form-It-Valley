import { json } from '@sveltejs/kit';
import { backendUrl } from '$lib/server/proxy';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params }) => {
	const res = await fetch(backendUrl(`/api/public/flows/slug/${params.slug}`));
	return json(await res.json(), { status: res.status });
};
