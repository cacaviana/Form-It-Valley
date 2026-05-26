/**
 * Textos da UI do formulario publico (/q/<slug>) editaveis por flow.
 * Cada chave tem um default; se o flow custom (ui_texts) tiver a chave, sobrescreve.
 *
 * Placeholders suportados: {{nome}}, {{email}}, {{data}}, {{horario}}, {{telefone}}, {{current}}, {{total}}.
 */
export interface UITexts {
  // Form
  form_label_name?: string;
  form_placeholder_name?: string;
  form_label_email?: string;
  form_placeholder_email?: string;
  form_label_whatsapp?: string;
  form_label_ddd?: string;
  form_placeholder_phone?: string;
  form_button_start?: string;
  form_powered_by?: string;

  // Questions
  questions_counter?: string;       // "Pergunta {{current}} / {{total}}"
  questions_button_next?: string;
  questions_button_back?: string;
  questions_placeholder_text?: string;
  questions_placeholder_number?: string;
  questions_yes?: string;
  questions_no?: string;

  // Calendar
  calendar_title?: string;
  calendar_subtitle?: string;
  calendar_back?: string;

  // Time
  time_title?: string;
  time_morning?: string;
  time_afternoon?: string;
  time_empty?: string;
  time_continue?: string;
  time_back?: string;

  // Confirm
  confirm_title?: string;
  confirm_subtitle?: string;
  confirm_label_name?: string;
  confirm_label_email?: string;
  confirm_label_phone?: string;
  confirm_label_date?: string;
  confirm_label_time?: string;
  confirm_button?: string;
  confirm_submitting?: string;
  confirm_back?: string;

  // Done (tela de sucesso)
  done_title?: string;
  done_subtitle?: string;          // "Agendamento confirmado! Evento criado no Google Calendar."
  done_gcal?: string;               // "Convite enviado para {{email}} via Google Calendar"
  done_email?: string;              // "E-mail enviado para {{email}}"
  done_whatsapp?: string;           // "WhatsApp enviado para {{telefone}}"
  done_thanks?: string;             // "Obrigado, {{nome}}!"
}

export const UI_TEXT_DEFAULTS: Required<UITexts> = {
  // Form
  form_label_name: 'Nome completo',
  form_placeholder_name: 'Seu nome completo',
  form_label_email: 'E-mail',
  form_placeholder_email: 'seu@email.com',
  form_label_whatsapp: 'WhatsApp',
  form_label_ddd: 'DDD',
  form_placeholder_phone: '99999-9999',
  form_button_start: 'Começar',
  form_powered_by: 'Powered by IT Valley School',

  // Questions
  questions_counter: 'Pergunta {{current}} / {{total}}',
  questions_button_next: 'Próximo',
  questions_button_back: 'Voltar',
  questions_placeholder_text: 'Sua resposta',
  questions_placeholder_number: 'Digite um número',
  questions_yes: 'Sim',
  questions_no: 'Não',

  // Calendar
  calendar_title: 'Escolha o dia',
  calendar_subtitle: 'Selecione uma data disponível',
  calendar_back: 'Voltar',

  // Time
  time_title: 'Escolha o horário',
  time_morning: 'Manhã',
  time_afternoon: 'Tarde',
  time_empty: 'Nenhum horário disponível nesta data',
  time_continue: 'Continuar',
  time_back: 'Voltar ao calendário',

  // Confirm
  confirm_title: 'Confirme seu agendamento',
  confirm_subtitle: 'Verifique os dados antes de confirmar',
  confirm_label_name: 'Nome',
  confirm_label_email: 'E-mail',
  confirm_label_phone: 'Telefone',
  confirm_label_date: 'Data',
  confirm_label_time: 'Horário',
  confirm_button: 'Confirmar Agendamento',
  confirm_submitting: 'Agendando...',
  confirm_back: 'Voltar',

  // Done
  done_title: 'Agendamento Confirmado!',
  done_subtitle: 'Agendamento confirmado! Evento criado no Google Calendar.',
  done_gcal: 'Convite enviado para {{email}} via Google Calendar',
  done_email: 'E-mail enviado para {{email}}',
  done_whatsapp: 'WhatsApp enviado para {{telefone}}',
  done_thanks: 'Obrigado, {{nome}}!'
};

export function resolveUiTexts(custom?: UITexts | null): Required<UITexts> {
  const c = custom || {};
  const out = { ...UI_TEXT_DEFAULTS };
  for (const key of Object.keys(UI_TEXT_DEFAULTS) as (keyof UITexts)[]) {
    const v = c[key];
    if (typeof v === 'string' && v.length > 0) {
      out[key] = v;
    }
  }
  return out;
}

export function interpolate(tpl: string, vars: Record<string, string | number>): string {
  return tpl.replace(/\{\{(\w+)\}\}/g, (_, k) => {
    const v = vars[k];
    return v != null ? String(v) : `{{${k}}}`;
  });
}

/** Mapa para apresentar os textos agrupados nos modais. */
export const FORM_TEXT_KEYS: { section: string; items: { key: keyof UITexts; label: string }[] }[] = [
  {
    section: 'Formulário inicial',
    items: [
      { key: 'form_label_name', label: 'Label "Nome completo"' },
      { key: 'form_placeholder_name', label: 'Placeholder do nome' },
      { key: 'form_label_email', label: 'Label "E-mail"' },
      { key: 'form_placeholder_email', label: 'Placeholder do e-mail' },
      { key: 'form_label_whatsapp', label: 'Label "WhatsApp"' },
      { key: 'form_label_ddd', label: 'Label "DDD"' },
      { key: 'form_placeholder_phone', label: 'Placeholder do telefone' },
      { key: 'form_button_start', label: 'Botão "Começar"' },
      { key: 'form_powered_by', label: 'Rodapé "Powered by..."' }
    ]
  },
  {
    section: 'Perguntas',
    items: [
      { key: 'questions_counter', label: 'Contador "Pergunta X / Y"' },
      { key: 'questions_button_next', label: 'Botão "Próximo"' },
      { key: 'questions_button_back', label: 'Botão "Voltar"' },
      { key: 'questions_placeholder_text', label: 'Placeholder de texto' },
      { key: 'questions_placeholder_number', label: 'Placeholder numérico' },
      { key: 'questions_yes', label: 'Botão "Sim"' },
      { key: 'questions_no', label: 'Botão "Não"' }
    ]
  }
];

export const SCHEDULING_TEXT_KEYS: { section: string; items: { key: keyof UITexts; label: string }[] }[] = [
  {
    section: 'Calendário (escolher dia)',
    items: [
      { key: 'calendar_title', label: 'Título "Escolha o dia"' },
      { key: 'calendar_subtitle', label: 'Subtítulo' },
      { key: 'calendar_back', label: 'Botão "Voltar"' }
    ]
  },
  {
    section: 'Horários',
    items: [
      { key: 'time_title', label: 'Título "Escolha o horário"' },
      { key: 'time_morning', label: 'Seção "Manhã"' },
      { key: 'time_afternoon', label: 'Seção "Tarde"' },
      { key: 'time_empty', label: 'Mensagem vazia' },
      { key: 'time_continue', label: 'Botão "Continuar"' },
      { key: 'time_back', label: 'Botão "Voltar ao calendário"' }
    ]
  },
  {
    section: 'Confirmação',
    items: [
      { key: 'confirm_title', label: 'Título' },
      { key: 'confirm_subtitle', label: 'Subtítulo' },
      { key: 'confirm_label_name', label: 'Label "Nome"' },
      { key: 'confirm_label_email', label: 'Label "E-mail"' },
      { key: 'confirm_label_phone', label: 'Label "Telefone"' },
      { key: 'confirm_label_date', label: 'Label "Data"' },
      { key: 'confirm_label_time', label: 'Label "Horário"' },
      { key: 'confirm_button', label: 'Botão "Confirmar"' },
      { key: 'confirm_submitting', label: 'Texto durante envio' },
      { key: 'confirm_back', label: 'Botão "Voltar"' }
    ]
  },
  {
    section: 'Sucesso (após confirmar)',
    items: [
      { key: 'done_title', label: 'Título "Agendamento Confirmado!"' },
      { key: 'done_subtitle', label: 'Mensagem de confirmação' },
      { key: 'done_gcal', label: 'Linha "Convite enviado"' },
      { key: 'done_email', label: 'Linha "E-mail enviado"' },
      { key: 'done_whatsapp', label: 'Linha "WhatsApp enviado"' },
      { key: 'done_thanks', label: 'Mensagem final "Obrigado, {{nome}}!"' }
    ]
  }
];
