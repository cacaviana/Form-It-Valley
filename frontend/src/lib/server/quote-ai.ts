import OpenAI from 'openai';
import { env } from '$env/dynamic/private';
import { getDb } from './db';

export async function generateQuote(payload: {
	flow_id: string;
	flow_slug: string;
	client_name: string;
	client_email: string;
	client_phone?: string;
	client_address?: string;
	answers: { node_id: string; question: string; value: string; label?: string }[];
	end_node_id: string;
}) {
	const db = await getDb();

	// 1. Load flow to get pricing_csv + business rules
	const flow = await db.collection('flows').findOne({ slug: payload.flow_slug });
	if (!flow) throw new Error('Flow not found');

	const endNode = flow.nodes?.find((n: any) => n.id === payload.end_node_id);
	const pricingCsv = flow.pricing_csv || endNode?.data?.businessContext || '';
	const aiInstruction = endNode?.data?.aiInstruction || '';

	// 2. Build context for AI
	const answersText = payload.answers
		.map((a) => `- ${a.question}: ${a.label || a.value}`)
		.join('\n');

	const prompt = `Tu es un expert en estimation de travaux. Génère un devis professionnel en JSON.

## CLIENT
Nom: ${payload.client_name}
Email: ${payload.client_email}
Téléphone: ${payload.client_phone || 'N/A'}
Adresse: ${payload.client_address || 'N/A'}

## RÉPONSES DU CLIENT
${answersText}

## CATALOGUE DE PRIX (utilise UNIQUEMENT ces prix)
${pricingCsv || 'Aucun catalogue fourni'}

## RÈGLES D'AFFAIRES
${aiInstruction || 'Aucune règle spécifique'}

## INSTRUCTIONS
- Utilise UNIQUEMENT les produits et prix du catalogue ci-dessus
- Si un produit n'est pas dans le catalogue, mets le prix à 0 et ajoute "(prix à consulter)"
- Calcule: TPS = 5%, TVQ = 9.975%
- Ne jamais inventer de prix

Réponds en JSON avec cette structure exacte:
{
  "items": [{"description": "nom du produit", "unit_price": 0.00, "quantity": 1, "subtotal": 0.00}],
  "subtotal": 0.00,
  "taxes_tps": 0.00,
  "taxes_tvq": 0.00,
  "total": 0.00,
  "recommendations": "texte",
  "notes": "texte"
}`;

	// 3. Call OpenAI
	const apiKey = env.OPENAI_API_KEY;
	if (!apiKey) throw new Error('OPENAI_API_KEY not configured');

	const openai = new OpenAI({ apiKey });
	const model = env.OPENAI_MODEL || 'gpt-4o-mini';

	const completion = await openai.chat.completions.create({
		model,
		messages: [
			{ role: 'system', content: 'Tu es un assistant qui génère des devis en JSON. Réponds UNIQUEMENT en JSON valide, sans markdown.' },
			{ role: 'user', content: prompt }
		],
		temperature: 0.1,
		max_tokens: 2000
	});

	const raw = completion.choices[0]?.message?.content || '';

	// 4. Parse JSON response
	let quoteData = null;
	let quoteText = raw;

	try {
		// Extract JSON from response (handle markdown code blocks)
		const jsonMatch = raw.match(/\{[\s\S]*\}/);
		if (jsonMatch) {
			quoteData = JSON.parse(jsonMatch[0]);

			// Validate and recalculate totals
			if (quoteData.items) {
				for (const item of quoteData.items) {
					item.subtotal = item.unit_price * item.quantity;
				}
				quoteData.subtotal = quoteData.items.reduce((s: number, i: any) => s + i.subtotal, 0);
				quoteData.taxes_tps = Math.round(quoteData.subtotal * 0.05 * 100) / 100;
				quoteData.taxes_tvq = Math.round(quoteData.subtotal * 0.09975 * 100) / 100;
				quoteData.total = Math.round((quoteData.subtotal + quoteData.taxes_tps + quoteData.taxes_tvq) * 100) / 100;
			}
		}
	} catch (e) {
		console.error('[QuoteAI] JSON parse error:', e);
	}

	// 5. Save submission to DB
	const doc = {
		tenant_id: 'tenant_1',
		flow_id: payload.flow_id,
		flow_slug: payload.flow_slug,
		client_name: payload.client_name,
		client_email: payload.client_email,
		client_phone: payload.client_phone || null,
		client_address: payload.client_address || null,
		answers: payload.answers,
		end_node_id: payload.end_node_id,
		end_type: 'quote',
		quote_text: quoteText,
		quote_data: quoteData,
		status: quoteData ? 'quoted' : 'pending',
		created_at: new Date().toISOString()
	};

	await db.collection('submissions').insertOne(doc);

	return {
		quote_text: quoteText,
		quote_data: quoteData
	};
}
