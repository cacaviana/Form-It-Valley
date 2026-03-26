import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

/** GET /api/whatsapp-templates — Lista templates disponiveis do microsservico */
export const GET: RequestHandler = async () => {
	const apiUrl = env.WHATSAPP_API_URL;
	const apiKey = env.WHATSAPP_API_KEY;

	if (!apiUrl || !apiKey) {
		return json({ error: 'WhatsApp nao configurado' }, { status: 503 });
	}

	try {
		const res = await fetch(`${apiUrl}/mensagens/templates`, {
			headers: { 'X-API-Key': apiKey }
		});

		if (!res.ok) {
			return json({ error: 'Erro ao buscar templates' }, { status: 502 });
		}

		const templates = await res.json();

		// Retorna so os aprovados com info util pro editor
		const formatted = templates
			.filter((t: any) => t.status === 'APPROVED')
			.map((t: any) => {
				const bodyComponent = t.components?.find((c: any) => c.type === 'BODY');
				const bodyText = bodyComponent?.text || '';
				// Conta variaveis {{1}}, {{2}}, etc
				const varCount = (bodyText.match(/\{\{\d+\}\}/g) || []).length;

				return {
					name: t.name,
					language: t.language,
					category: t.category,
					body: bodyText,
					variableCount: varCount
				};
			});

		return json(formatted);
	} catch (e) {
		console.error('[WhatsApp Templates] Erro:', e);
		return json({ error: 'Erro de conexao' }, { status: 502 });
	}
};
