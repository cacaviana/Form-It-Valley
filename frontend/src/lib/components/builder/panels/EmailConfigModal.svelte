<script lang="ts">
  import type { EmailConfig } from '$lib/dto/flows/types';

  let {
    open,
    value,
    themeColor = 'violet',
    onSave,
    onCancel
  } = $props<{
    open: boolean;
    value: EmailConfig | null;
    themeColor?: string;
    onSave: (v: EmailConfig | null) => void;
    onCancel: () => void;
  }>();

  const DEFAULTS: Required<EmailConfig> = {
    subject: 'Agendamento confirmado - {{data}} as {{horario}}',
    header_title: 'Agendamento Confirmado!',
    header_subtitle: 'IT Valley - Escola de Tecnologia',
    greeting: 'Olá, <strong>{{nome}}</strong>!',
    body: 'Seu atendimento foi agendado com sucesso.',
    meet_button_text: 'Entrar na Reunião (Google Meet)',
    calendar_button_text: 'Ver Evento no Google Calendar',
    footer: 'IT Valley School - Escola de Tecnologia',
    header_color: '#2563eb'
  };

  const themeColorMap: Record<string, string> = {
    violet: '#7C3AED', blue: '#2563EB', emerald: '#059669', rose: '#E11D48',
    orange: '#EA580C', cyan: '#0891B2', amber: '#D97706', slate: '#334155'
  };

  // Estado local
  let useDefault = $state(value === null);
  let local = $state<Required<EmailConfig>>({ ...DEFAULTS });

  $effect(() => {
    const _value = value;
    const _theme = themeColor;
    if (!open) return;
    useDefault = _value == null;
    if (_value) {
      local = {
        subject: _value.subject ?? DEFAULTS.subject,
        header_title: _value.header_title ?? DEFAULTS.header_title,
        header_subtitle: _value.header_subtitle ?? DEFAULTS.header_subtitle,
        greeting: _value.greeting ?? DEFAULTS.greeting,
        body: _value.body ?? DEFAULTS.body,
        meet_button_text: _value.meet_button_text ?? DEFAULTS.meet_button_text,
        calendar_button_text: _value.calendar_button_text ?? DEFAULTS.calendar_button_text,
        footer: _value.footer ?? DEFAULTS.footer,
        header_color: _value.header_color ?? themeColorMap[_theme] ?? DEFAULTS.header_color
      };
    } else {
      local = { ...DEFAULTS, header_color: themeColorMap[_theme] ?? DEFAULTS.header_color };
    }
  });

  // Sample pra preview
  const SAMPLE = {
    nome: 'Henrique Proscholdt',
    data: 'quinta-feira, 28 de maio de 2026',
    horario: '10:00',
    link: 'https://meet.google.com/abc-defg-hij',
    email: 'henrique@example.com'
  };

  function resolvePlaceholders(tpl: string): string {
    return tpl.replace(/\{\{(\w+)\}\}/g, (_, key) => (SAMPLE as Record<string, string>)[key] ?? `{{${key}}}`);
  }

  let preview = $derived({
    subject: resolvePlaceholders(local.subject),
    header_title: resolvePlaceholders(local.header_title),
    header_subtitle: resolvePlaceholders(local.header_subtitle),
    greeting: resolvePlaceholders(local.greeting),
    body: resolvePlaceholders(local.body),
    meet_button_text: local.meet_button_text,
    calendar_button_text: local.calendar_button_text,
    footer: resolvePlaceholders(local.footer)
  });

  function save() {
    if (useDefault) {
      onSave(null);
    } else {
      onSave({ ...local });
    }
  }

  function restoreDefaults() {
    local = { ...DEFAULTS, header_color: themeColorMap[themeColor] ?? DEFAULTS.header_color };
  }

  const placeholders = [
    { key: '{{nome}}', label: 'Nome do lead' },
    { key: '{{data}}', label: 'Data formatada' },
    { key: '{{horario}}', label: 'Horário' },
    { key: '{{link}}', label: 'Link da reunião' },
    { key: '{{email}}', label: 'E-mail do lead' }
  ];
</script>

{#if open}
  <div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-stretch md:items-center justify-center p-0 md:p-6">
    <div class="bg-white w-full md:max-w-6xl md:rounded-2xl shadow-2xl flex flex-col max-h-screen overflow-hidden">

      <!-- Header -->
      <div class="px-5 py-3 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
        <div>
          <h2 class="text-base font-semibold text-gray-900">E-mail de confirmação</h2>
          <p class="text-xs text-gray-500">Personalize o e-mail enviado ao lead após confirmar o agendamento</p>
        </div>
        <button onclick={onCancel} class="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-400 hover:text-gray-700 cursor-pointer transition-colors" aria-label="Fechar">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <!-- Body 2 colunas -->
      <div class="flex-1 flex flex-col md:flex-row overflow-hidden">

        <!-- Esquerda: controles -->
        <aside class="w-full md:w-[400px] flex-shrink-0 border-r border-gray-200 overflow-y-auto bg-gray-50/50">
          <div class="p-5 space-y-4">

            <!-- Toggle usar default -->
            <div class="flex items-start gap-3 bg-white border border-gray-200 rounded-xl p-3">
              <button
                type="button"
                onclick={() => (useDefault = !useDefault)}
                class="relative inline-flex items-center flex-shrink-0 h-6 w-11 rounded-full transition-colors cursor-pointer mt-0.5 {useDefault ? 'bg-blue-600' : 'bg-gray-300'}"
                role="switch"
                aria-checked={useDefault}
                aria-label="Usar template padrão"
              >
                <span class="inline-block w-4 h-4 bg-white rounded-full shadow transform transition-transform {useDefault ? 'translate-x-6' : 'translate-x-1'}"></span>
              </button>
              <div class="flex-1">
                <div class="text-sm font-semibold text-gray-800">Usar e-mail padrão</div>
                <p class="text-xs text-gray-500 mt-0.5">Quando ligado, o flow usa o template global do sistema.</p>
              </div>
            </div>

            {#if !useDefault}
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-gray-700 uppercase tracking-wide">Conteúdo personalizado</span>
                <button type="button" onclick={restoreDefaults} class="text-[11px] text-blue-600 hover:text-blue-800 underline cursor-pointer">
                  Restaurar padrão
                </button>
              </div>

              <!-- Placeholders disponíveis -->
              <div class="bg-blue-50 border border-blue-100 rounded-lg px-3 py-2">
                <p class="text-[11px] font-semibold text-blue-800 mb-1">Placeholders disponíveis (clique p/ copiar):</p>
                <div class="flex flex-wrap gap-1">
                  {#each placeholders as p}
                    <button
                      type="button"
                      class="text-[10px] bg-white border border-blue-200 text-blue-700 px-1.5 py-0.5 rounded font-mono hover:bg-blue-100 cursor-pointer"
                      title={p.label}
                      onclick={() => navigator.clipboard.writeText(p.key)}
                    >{p.key}</button>
                  {/each}
                </div>
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-subject">Assunto</label>
                <input id="ec-subject" type="text" bind:value={local.subject} class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400" />
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-title">Título do header</label>
                <input id="ec-title" type="text" bind:value={local.header_title} class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400" />
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-subtitle">Subtítulo do header</label>
                <input id="ec-subtitle" type="text" bind:value={local.header_subtitle} class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400" />
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-color">Cor do header</label>
                <div class="flex items-center gap-2">
                  <input id="ec-color" type="color" bind:value={local.header_color} class="h-9 w-12 rounded border border-gray-200 cursor-pointer bg-white" />
                  <input type="text" bind:value={local.header_color} class="flex-1 border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400 font-mono" />
                </div>
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-greeting">Saudação</label>
                <input id="ec-greeting" type="text" bind:value={local.greeting} class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400" />
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-body">Mensagem principal</label>
                <textarea id="ec-body" bind:value={local.body} class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400 h-16 resize-y"></textarea>
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-meet">Texto do botão Meet</label>
                <input id="ec-meet" type="text" bind:value={local.meet_button_text} class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400" />
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-cal">Texto do botão Calendar</label>
                <input id="ec-cal" type="text" bind:value={local.calendar_button_text} class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400" />
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-600 uppercase tracking-wide mb-1" for="ec-footer">Rodapé</label>
                <input id="ec-footer" type="text" bind:value={local.footer} class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-xs bg-white outline-none focus:border-blue-400" />
              </div>
            {/if}
          </div>
        </aside>

        <!-- Direita: preview -->
        <main class="flex-1 overflow-y-auto bg-gray-100">
          <div class="px-4 py-3 border-b border-gray-200 bg-white flex items-center gap-2 sticky top-0 z-10">
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            <div class="flex-1">
              <p class="text-xs font-medium text-gray-600 uppercase tracking-wide">Preview do e-mail</p>
              <p class="text-[11px] text-gray-400 mt-0.5"><strong>Assunto:</strong> {preview.subject}</p>
            </div>
          </div>

          <div class="p-6">
            <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
              <div style="background: {local.header_color}; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
                <h2 style="margin: 0; font-size: 20px;">{preview.header_title}</h2>
                <p style="margin: 8px 0 0; opacity: 0.85; font-size: 13px;">{preview.header_subtitle}</p>
              </div>
              <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p style="color: #374151; font-size: 15px;">{@html preview.greeting}</p>
                <p style="color: #6b7280; font-size: 14px;">{preview.body}</p>
                <div style="background: white; border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; margin: 16px 0;">
                  <p style="margin: 0 0 8px; color: #374151;"><strong>Data:</strong> {SAMPLE.data}</p>
                  <p style="margin: 0; color: #374151;"><strong>Horario:</strong> {SAMPLE.horario}</p>
                </div>
                <div style="display: block; background: #00897b; color: white; text-align: center; padding: 12px; border-radius: 8px; font-weight: 600; font-size: 14px;">{preview.meet_button_text}</div>
                <div style="display: block; background: {local.header_color}; color: white; text-align: center; padding: 12px; border-radius: 8px; font-weight: 600; font-size: 14px; margin-top: 8px;">{preview.calendar_button_text}</div>
                <p style="color: #9ca3af; font-size: 12px; margin-top: 16px; text-align: center;">{preview.footer}</p>
              </div>
            </div>
          </div>
        </main>
      </div>

      <!-- Footer -->
      <div class="px-5 py-3 border-t border-gray-200 flex items-center justify-end gap-2 flex-shrink-0 bg-white">
        <button type="button" onclick={onCancel} class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors">
          Cancelar
        </button>
        <button type="button" onclick={save} class="px-4 py-2 text-sm font-semibold text-white rounded-lg cursor-pointer transition-colors bg-blue-600 hover:bg-blue-700 active:scale-[0.98]">
          Salvar
        </button>
      </div>
    </div>
  </div>
{/if}
