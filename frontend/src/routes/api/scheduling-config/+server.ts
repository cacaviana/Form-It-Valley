import { json } from '@sveltejs/kit';
import { getDb } from '$lib/server/db';
import type { RequestHandler } from './$types';

const CONFIG_ID = 'scheduling_config';

export const GET: RequestHandler = async () => {
	const db = await getDb();
	const config = await db.collection('settings').findOne({ _id: CONFIG_ID });
	return json({
		morning_slots: config?.morning_slots ?? 3,
		afternoon_slots: config?.afternoon_slots ?? 3
	});
};

export const PUT: RequestHandler = async ({ request }) => {
	const body = await request.json();
	const db = await getDb();
	await db.collection('settings').updateOne(
		{ _id: CONFIG_ID },
		{
			$set: {
				morning_slots: body.morning_slots ?? 3,
				afternoon_slots: body.afternoon_slots ?? 3,
				updated_at: new Date().toISOString()
			}
		},
		{ upsert: true }
	);
	return json({ morning_slots: body.morning_slots, afternoon_slots: body.afternoon_slots });
};
