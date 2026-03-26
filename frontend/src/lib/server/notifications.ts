import { env } from '$env/dynamic/private';

/**
 * Envia e-mail de confirmacao de agendamento via Resend.
 * O lead recebe email com data/horario e link do evento no Google Calendar.
 */
export async function sendSchedulingEmail(data: {
	leadName: string;
	leadEmail: string;
	scheduledDate: string;
	scheduledTime: string;
	calendarLink: string;
}): Promise<boolean> {
	const apiKey = env.RESEND_API_KEY;
	if (!apiKey) {
		console.warn('[Notifications] RESEND_API_KEY nao configurada — e-mail nao enviado');
		return false;
	}

	const fromEmail = env.EMAIL_FROM || 'onboarding@resend.dev';
	const formattedDate = formatDatePtBR(data.scheduledDate);

	const htmlBody = `
		<div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
			<div style="background: #2563eb; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
				<h2 style="margin: 0;">Agendamento Confirmado!</h2>
				<p style="margin: 8px 0 0; opacity: 0.85;">IT Valley - Escola de Tecnologia</p>
			</div>
			<div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
				<p style="color: #374151; font-size: 15px;">Ola, <strong>${data.leadName}</strong>!</p>
				<p style="color: #6b7280; font-size: 14px;">Seu atendimento foi agendado com sucesso.</p>
				<div style="background: white; border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; margin: 16px 0;">
					<p style="margin: 0 0 8px; color: #374151;"><strong>Data:</strong> ${formattedDate}</p>
					<p style="margin: 0; color: #374151;"><strong>Horario:</strong> ${data.scheduledTime}</p>
				</div>
				${data.calendarLink ? `<a href="${data.calendarLink}" style="display: block; background: #2563eb; color: white; text-align: center; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px;">Ver Evento no Google Calendar</a>` : ''}
				<p style="color: #9ca3af; font-size: 12px; margin-top: 16px; text-align: center;">
					IT Valley School - Escola de Tecnologia
				</p>
			</div>
		</div>
	`;

	try {
		const res = await fetch('https://api.resend.com/emails', {
			method: 'POST',
			headers: {
				'Authorization': `Bearer ${apiKey}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				from: fromEmail,
				to: [data.leadEmail],
				subject: `Agendamento confirmado - ${formattedDate} as ${data.scheduledTime}`,
				html: htmlBody
			})
		});

		if (res.ok) {
			const result = await res.json();
			console.log(`[Notifications] E-mail enviado para ${data.leadEmail} — id: ${result.id}`);
			return true;
		} else {
			const err = await res.text();
			console.error('[Notifications] Erro ao enviar e-mail:', err);
			return false;
		}
	} catch (e) {
		console.error('[Notifications] Erro ao enviar e-mail:', e);
		return false;
	}
}

/**
 * Envia mensagem WhatsApp de confirmacao via microsservico IT Valley.
 * API: POST /mensagens/enviar (template-based, Meta WhatsApp Business)
 *
 * Contrato do microsservico:
 *   - Header: X-API-Key
 *   - Body: { nome, telefone, template_name, language, country_code, variaveis[] }
 *   - country_code: ISO do pais (BR, CA, US, PT...) — NAO o codigo numerico
 *   - telefone: com codigo do pais na frente (5527..., 1581...)
 *     IMPORTANTE: DDDs brasileiros como 44 conflitam com codigo UK,
 *     entao sempre enviar com 55 na frente para BR
 *   - variaveis: SEM quebra de linha (\n) — Meta API rejeita
 *
 * Requer no .env:
 *   WHATSAPP_API_URL
 *   WHATSAPP_API_KEY
 *   WHATSAPP_TEMPLATE_NAME (default: teste0004)
 */
export async function sendWhatsAppNotification(data: {
	leadName: string;
	leadPhone: string;
	leadEmail?: string;
	scheduledDate: string;
	scheduledTime: string;
	calendarLink: string;
	templateName?: string;
	templateVariables?: string[];
}): Promise<boolean> {
	const apiUrl = env.WHATSAPP_API_URL;
	const apiKey = env.WHATSAPP_API_KEY;
	const defaultTemplate = env.WHATSAPP_TEMPLATE_NAME || 'teste0004';
	const template = data.templateName || defaultTemplate;

	if (!apiUrl || !apiKey) {
		console.warn('[Notifications] WHATSAPP_API_URL ou WHATSAPP_API_KEY nao configurada — WhatsApp nao enviado');
		return false;
	}

	const { phone, countryCode } = normalizePhone(data.leadPhone);
	if (!phone) {
		console.warn('[Notifications] Telefone invalido, WhatsApp nao enviado');
		return false;
	}

	const formattedDate = formatDatePtBR(data.scheduledDate);

	// Resolve placeholders nas variaveis configuradas pelo admin
	// ou usa o fallback padrao se nao configurou
	let variaveis: string[];

	if (data.templateVariables && data.templateVariables.length > 0) {
		variaveis = data.templateVariables.map(v => resolvePlaceholders(v, {
			nome: data.leadName,
			data: formattedDate,
			horario: data.scheduledTime,
			link: data.calendarLink || 'Sera enviado por e-mail',
			email: data.leadEmail || '',
			telefone: data.leadPhone
		}));
	} else {
		variaveis = [
			data.leadName,
			`Seu atendimento na IT Valley foi confirmado! Data: ${formattedDate} - Horario: ${data.scheduledTime}`,
			data.calendarLink
				? `Acesse o link da reuniao: ${data.calendarLink}`
				: 'Voce recebera o link da reuniao por e-mail. Ate la!'
		];
	}

	// Meta API NAO aceita \n, \t ou 4+ espacos consecutivos
	variaveis = variaveis.map(v => v.replace(/[\n\t]/g, ' ').replace(/\s{4,}/g, '   '));

	const payload = {
		nome: data.leadName,
		telefone: phone,
		template_name: template,
		language: 'pt_BR',
		country_code: countryCode,
		variaveis
	};

	try {
		console.log(`[Notifications] Enviando WhatsApp para ${phone} (${countryCode}) via template ${template}`);

		const res = await fetch(`${apiUrl}/mensagens/enviar`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-API-Key': apiKey
			},
			body: JSON.stringify(payload)
		});

		if (res.ok) {
			const result = await res.json();
			console.log(`[Notifications] WhatsApp queued — message_id: ${result.message_id}, status: ${result.status}`);
			return true;
		} else {
			const err = await res.text();
			console.error('[Notifications] Erro ao enviar WhatsApp:', err);
			return false;
		}
	} catch (e) {
		console.error('[Notifications] Erro ao enviar WhatsApp:', e);
		return false;
	}
}

/**
 * Normaliza telefone e detecta pais.
 *
 * Formatos aceitos:
 *   BR: "27995130691", "5527995130691", "+55 27 99513-0691"
 *   CA/US: "+1 (581) 578-0564", "15815780564", "5815780564"
 *
 * Retorna telefone com codigo do pais e o country_code ISO.
 */
function normalizePhone(phone: string): { phone: string; countryCode: string } {
	const digits = phone.replace(/\D/g, '');

	// +55 ou 55 na frente → Brasil (13 digitos)
	if (digits.length === 13 && digits.startsWith('55')) {
		return { phone: digits, countryCode: 'BR' };
	}

	// +1 na frente → Canada/US (11 digitos: 1 + 10)
	if (digits.length === 11 && digits.startsWith('1')) {
		return { phone: digits, countryCode: 'CA' };
	}

	// 11 digitos sem prefixo internacional → Brasil (DDD + 9 + 8 digitos)
	if (digits.length === 11 && !digits.startsWith('1')) {
		return { phone: `55${digits}`, countryCode: 'BR' };
	}

	// 10 digitos → pode ser CA/US (sem o 1) ou BR sem o 9
	if (digits.length === 10) {
		// Heuristica: DDDs brasileiros vao de 11 a 99.
		// Numeros CA/US area codes vao de 2xx a 9xx.
		// Se comeca com digito >= 2 e o terceiro digito nao e 9, assume CA/US
		// Mas a forma mais segura: se o lead digitou 10 digitos,
		// assume BR (DDD + 8 digitos, falta o 9)
		const ddd = digits.slice(0, 2);
		const num = digits.slice(2);
		return { phone: `55${ddd}9${num}`, countryCode: 'BR' };
	}

	// 12 digitos: 55 + DDD + 8 digitos (BR sem o 9)
	if (digits.length === 12 && digits.startsWith('55')) {
		const ddd = digits.slice(2, 4);
		const num = digits.slice(4);
		return { phone: `55${ddd}9${num}`, countryCode: 'BR' };
	}

	// Fallback: tenta detectar pelo prefixo
	if (digits.startsWith('55') && digits.length >= 12) {
		return { phone: digits, countryCode: 'BR' };
	}
	if (digits.startsWith('1') && digits.length >= 11) {
		return { phone: digits, countryCode: 'CA' };
	}

	// Ultimo recurso: assume BR e adiciona 55
	if (digits.length >= 10) {
		return { phone: `55${digits}`, countryCode: 'BR' };
	}

	return { phone: '', countryCode: '' };
}

/** Substitui placeholders {{nome}}, {{data}}, etc. pelo valor real */
function resolvePlaceholders(template: string, values: Record<string, string>): string {
	return template.replace(/\{\{(\w+)\}\}/g, (match, key) => values[key] || match);
}

/** Formata data YYYY-MM-DD para formato brasileiro */
function formatDatePtBR(dateStr: string): string {
	const [y, m, d] = dateStr.split('-').map(Number);
	return new Date(y, m - 1, d).toLocaleDateString('pt-BR', {
		weekday: 'long',
		day: 'numeric',
		month: 'long',
		year: 'numeric'
	});
}
