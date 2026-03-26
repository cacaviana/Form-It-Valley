import { json, error } from '@sveltejs/kit';
import { generateQuote } from '$lib/server/quote-ai';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	const body = await request.json();

	try {
		const result = await generateQuote(body);
		return json(result);
	} catch (e: any) {
		console.error('[generate-quote] Error:', e.message);
		throw error(500, `Erreur lors de la génération du devis: ${e.message}`);
	}
};
