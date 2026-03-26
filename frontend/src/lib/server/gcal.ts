import { google } from 'googleapis';
import { env } from '$env/dynamic/private';

const SCOPES = ['https://www.googleapis.com/auth/calendar'];

function getCalendarService() {
	const jsonStr = env.GOOGLE_SERVICE_ACCOUNT_JSON;
	if (!jsonStr) throw new Error('GOOGLE_SERVICE_ACCOUNT_JSON not set');

	const credentials = JSON.parse(jsonStr);
	const auth = new google.auth.JWT(
		credentials.client_email,
		undefined,
		credentials.private_key,
		SCOPES
	);

	return google.calendar({ version: 'v3', auth });
}

function getCalendarId(): string {
	return env.GOOGLE_CALENDAR_ID || 'primary';
}

/** Get busy times for a date and return available slots */
export async function getAvailableSlots(dateStr: string): Promise<string[]> {
	const ALL_SLOTS = [
		'09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
		'14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30'
	];

	try {
		const calendar = getCalendarService();
		const calId = getCalendarId();

		const res = await calendar.events.list({
			calendarId: calId,
			timeMin: `${dateStr}T00:00:00-03:00`,
			timeMax: `${dateStr}T23:59:59-03:00`,
			singleEvents: true,
			orderBy: 'startTime',
			timeZone: 'America/Sao_Paulo'
		});

		const events = res.data.items || [];

		// Build busy intervals as HH:MM strings
		const busy: { start: string; end: string }[] = [];
		for (const event of events) {
			const start = event.start?.dateTime;
			const end = event.end?.dateTime;
			if (start && end) {
				// Extract HH:MM from ISO datetime
				const startTime = new Date(start).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' });
				const endTime = new Date(end).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' });
				busy.push({ start: startTime, end: endTime });
			}
		}

		// Filter available slots
		return ALL_SLOTS.filter(slot => {
			const [h, m] = slot.split(':').map(Number);
			const slotEnd = `${String(h + (m + 30 >= 60 ? 1 : 0)).padStart(2, '0')}:${String((m + 30) % 60).padStart(2, '0')}`;

			for (const b of busy) {
				if (slot < b.end && slotEnd > b.start) return false;
			}
			return true;
		});
	} catch (e) {
		console.error('[GCal] Error getting slots:', e);
		// Fallback to all slots on error
		return ALL_SLOTS;
	}
}

/** Get available dates for a month (checking Google Calendar) */
export async function getAvailableDates(month: number, year: number): Promise<{ date: string; available: boolean; slots_count: number }[]> {
	const ALL_SLOTS_COUNT = 14; // total possible slots per day
	const daysInMonth = new Date(year, month, 0).getDate();
	const today = new Date();
	today.setHours(0, 0, 0, 0);

	try {
		const calendar = getCalendarService();
		const calId = getCalendarId();

		const startDate = `${year}-${String(month).padStart(2, '0')}-01T00:00:00-03:00`;
		const endDate = `${year}-${String(month).padStart(2, '0')}-${daysInMonth}T23:59:59-03:00`;

		const res = await calendar.events.list({
			calendarId: calId,
			timeMin: startDate,
			timeMax: endDate,
			singleEvents: true,
			orderBy: 'startTime',
			timeZone: 'America/Sao_Paulo'
		});

		const events = res.data.items || [];

		// Count events per day
		const eventsPerDay: Record<string, number> = {};
		for (const event of events) {
			const start = event.start?.dateTime || event.start?.date;
			if (start) {
				const dayStr = start.slice(0, 10);
				eventsPerDay[dayStr] = (eventsPerDay[dayStr] || 0) + 1;
			}
		}

		const dates = [];
		for (let day = 1; day <= daysInMonth; day++) {
			const d = new Date(year, month - 1, day);
			const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
			const isWeekday = d.getDay() > 0 && d.getDay() < 6;
			const isFuture = d >= today;
			const dayEvents = eventsPerDay[dateStr] || 0;
			const freeSlots = Math.max(0, ALL_SLOTS_COUNT - dayEvents);

			dates.push({
				date: dateStr,
				available: isWeekday && isFuture && freeSlots > 0,
				slots_count: isWeekday && isFuture ? freeSlots : 0
			});
		}
		return dates;
	} catch (e) {
		console.error('[GCal] Error getting dates:', e);
		// Fallback: return weekdays as available
		const dates = [];
		for (let day = 1; day <= daysInMonth; day++) {
			const d = new Date(year, month - 1, day);
			const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
			const isWeekday = d.getDay() > 0 && d.getDay() < 6;
			const isFuture = d >= today;
			dates.push({ date: dateStr, available: isWeekday && isFuture, slots_count: isWeekday && isFuture ? ALL_SLOTS_COUNT : 0 });
		}
		return dates;
	}
}

/** Create an event on Google Calendar */
export async function createCalendarEvent(data: {
	leadName: string;
	leadEmail: string;
	leadPhone: string;
	scheduledDate: string;
	scheduledTime: string;
}): Promise<{ eventId: string; htmlLink: string } | null> {
	try {
		const calendar = getCalendarService();
		const calId = getCalendarId();

		const [h, m] = data.scheduledTime.split(':').map(Number);
		const endH = h + (m + 30 >= 60 ? 1 : 0);
		const endM = (m + 30) % 60;
		const endTime = `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`;

		const event = {
			summary: `Call Vendas - ${data.leadName}`,
			description: [
				`Lead: ${data.leadName}`,
				`Email: ${data.leadEmail}`,
				`Telefone: ${data.leadPhone || 'N/A'}`,
				``,
				`Agendado via FlowQuote`
			].join('\n'),
			start: {
				dateTime: `${data.scheduledDate}T${data.scheduledTime}:00`,
				timeZone: 'America/Sao_Paulo'
			},
			end: {
				dateTime: `${data.scheduledDate}T${endTime}:00`,
				timeZone: 'America/Sao_Paulo'
			},
			attendees: [{ email: data.leadEmail }],
			reminders: {
				useDefault: false,
				overrides: [
					{ method: 'email', minutes: 60 },
					{ method: 'popup', minutes: 30 }
				]
			}
		};

		const res = await calendar.events.insert({
			calendarId: calId,
			requestBody: event,
			sendUpdates: 'all'
		});

		return {
			eventId: res.data.id || '',
			htmlLink: res.data.htmlLink || ''
		};
	} catch (e) {
		console.error('[GCal] Error creating event:', e);
		return null;
	}
}
