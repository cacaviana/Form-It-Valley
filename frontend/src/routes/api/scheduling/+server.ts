import { json } from '@sveltejs/kit';
import { getDb } from '$lib/server/db';
import { getAvailableDates, getAvailableSlots, createCalendarEvent } from '$lib/server/gcal';
import { sendSchedulingEmail, sendWhatsAppNotification } from '$lib/server/notifications';
import type { RequestHandler } from './$types';

/** GET /api/scheduling?action=dates&month=3&year=2026  or  ?action=slots&date=2026-03-25 */
export const GET: RequestHandler = async ({ url }) => {
	const action = url.searchParams.get('action');

	if (action === 'dates') {
		const month = parseInt(url.searchParams.get('month') || '0');
		const year = parseInt(url.searchParams.get('year') || '0');
		if (!month || !year) return json({ error: 'month and year required' }, { status: 400 });

		const dates = await getAvailableDates(month, year);
		return json(dates);
	}

	if (action === 'slots') {
		const date = url.searchParams.get('date');
		if (!date) return json({ error: 'date required' }, { status: 400 });

		const slots = await getAvailableSlots(date);
		return json(slots);
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

/** POST /api/scheduling — Create event on Google Calendar + send WhatsApp */
export const POST: RequestHandler = async ({ request }) => {
	const body = await request.json();
	const db = await getDb();

	// 1. Create Google Calendar event (also sends email invite to lead via sendUpdates: 'all')
	const gcalResult = await createCalendarEvent({
		leadName: body.lead_name,
		leadEmail: body.lead_email,
		leadPhone: body.lead_phone || '',
		scheduledDate: body.scheduled_date,
		scheduledTime: body.scheduled_time
	});

	const calendarLink = gcalResult?.htmlLink || '';

	// 2. Send email and WhatsApp in parallel
	const [emailSent, whatsappSent] = await Promise.all([
		sendSchedulingEmail({
			leadName: body.lead_name,
			leadEmail: body.lead_email,
			scheduledDate: body.scheduled_date,
			scheduledTime: body.scheduled_time,
			calendarLink
		}),
		body.lead_phone
			? sendWhatsAppNotification({
				leadName: body.lead_name,
				leadPhone: body.lead_phone,
				leadEmail: body.lead_email,
				scheduledDate: body.scheduled_date,
				scheduledTime: body.scheduled_time,
				calendarLink,
				templateName: body.whatsapp_template || undefined,
				templateVariables: body.whatsapp_variables || undefined
			})
			: Promise.resolve(false)
	]);

	// 3. Save to database
	const doc = {
		flow_id: body.flow_id || null,
		flow_slug: body.flow_slug || null,
		lead_name: body.lead_name,
		lead_email: body.lead_email,
		lead_phone: body.lead_phone || null,
		lead_address: body.lead_address || null,
		qualifying_answers: body.qualifying_answers || [],
		scheduled_date: body.scheduled_date,
		scheduled_time: body.scheduled_time,
		timezone: 'America/Sao_Paulo',
		duration_minutes: 30,
		gcal_event_id: gcalResult?.eventId || null,
		gcal_event_link: calendarLink || null,
		email_sent: emailSent,
		whatsapp_sent: whatsappSent,
		status: 'confirmed',
		created_at: new Date().toISOString()
	};

	const result = await db.collection('scheduling').insertOne(doc);

	return json({
		id: result.insertedId.toString(),
		...doc,
		message: gcalResult
			? 'Agendamento confirmado! Evento criado no Google Calendar.'
			: 'Agendamento confirmado! Voce recebera uma confirmacao em breve.',
		gcal_event_link: calendarLink || undefined,
		email_sent: emailSent,
		whatsapp_sent: whatsappSent
	}, { status: 201 });
};
