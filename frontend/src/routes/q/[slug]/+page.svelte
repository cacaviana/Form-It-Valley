<script lang="ts">
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { FlowsService } from '$lib/services/flows.service';
  import { SubmissionsService } from '$lib/services/submissions.service';
  import type { Flow, FlowNode, FlowEdge } from '$lib/dto/flows/types';
  import utmTrackingScript from '$lib/scripts/utm-tracking.js?raw';

  const flowService = new FlowsService();
  const submissionService = new SubmissionsService();

  let flow = $state<Flow | null>(null);
  let loading = $state(true);
  let error = $state('');

  // Mapa de cores do tema
  const colorMap: Record<string, { main: string; gradient: string; gradientHeader: string; ring: string; bg: string; text: string; hover: string; lightBg: string }> = {
    violet:  { main: '#7C3AED', gradient: 'linear-gradient(135deg, #7C3AED, #9333EA)', gradientHeader: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)', ring: 'focus:ring-violet-500/25 focus:border-violet-400', bg: 'bg-violet-600 hover:bg-violet-700', text: 'text-violet-600', hover: 'hover:bg-violet-50', lightBg: 'bg-violet-50' },
    blue:    { main: '#2563EB', gradient: 'linear-gradient(135deg, #2563EB, #3B82F6)', gradientHeader: 'linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)', ring: 'focus:ring-blue-500/25 focus:border-blue-400', bg: 'bg-blue-600 hover:bg-blue-700', text: 'text-blue-600', hover: 'hover:bg-blue-50', lightBg: 'bg-blue-50' },
    emerald: { main: '#059669', gradient: 'linear-gradient(135deg, #059669, #10B981)', gradientHeader: 'linear-gradient(135deg, #059669 0%, #10B981 100%)', ring: 'focus:ring-emerald-500/25 focus:border-emerald-400', bg: 'bg-emerald-600 hover:bg-emerald-700', text: 'text-emerald-600', hover: 'hover:bg-emerald-50', lightBg: 'bg-emerald-50' },
    rose:    { main: '#E11D48', gradient: 'linear-gradient(135deg, #E11D48, #F43F5E)', gradientHeader: 'linear-gradient(135deg, #E11D48 0%, #F43F5E 100%)', ring: 'focus:ring-rose-500/25 focus:border-rose-400', bg: 'bg-rose-600 hover:bg-rose-700', text: 'text-rose-600', hover: 'hover:bg-rose-50', lightBg: 'bg-rose-50' },
    orange:  { main: '#EA580C', gradient: 'linear-gradient(135deg, #EA580C, #F97316)', gradientHeader: 'linear-gradient(135deg, #EA580C 0%, #F97316 100%)', ring: 'focus:ring-orange-500/25 focus:border-orange-400', bg: 'bg-orange-600 hover:bg-orange-700', text: 'text-orange-600', hover: 'hover:bg-orange-50', lightBg: 'bg-orange-50' },
    cyan:    { main: '#0891B2', gradient: 'linear-gradient(135deg, #0891B2, #06B6D4)', gradientHeader: 'linear-gradient(135deg, #0891B2 0%, #06B6D4 100%)', ring: 'focus:ring-cyan-500/25 focus:border-cyan-400', bg: 'bg-cyan-600 hover:bg-cyan-700', text: 'text-cyan-600', hover: 'hover:bg-cyan-50', lightBg: 'bg-cyan-50' },
    amber:   { main: '#D97706', gradient: 'linear-gradient(135deg, #D97706, #F59E0B)', gradientHeader: 'linear-gradient(135deg, #D97706 0%, #F59E0B 100%)', ring: 'focus:ring-amber-500/25 focus:border-amber-400', bg: 'bg-amber-600 hover:bg-amber-700', text: 'text-amber-600', hover: 'hover:bg-amber-50', lightBg: 'bg-amber-50' },
    slate:   { main: '#334155', gradient: 'linear-gradient(135deg, #334155, #475569)', gradientHeader: 'linear-gradient(135deg, #334155 0%, #475569 100%)', ring: 'focus:ring-slate-500/25 focus:border-slate-400', bg: 'bg-slate-600 hover:bg-slate-700', text: 'text-slate-600', hover: 'hover:bg-slate-50', lightBg: 'bg-slate-50' },
  };
  let theme = $derived(colorMap[flow?.theme_color || 'violet'] || colorMap.violet);

  // Executor state
  let phase = $state<'form' | 'questions' | 'end' | 'scheduling'>('form');
  let clientData = $state({ name: '', email: '', phone: '', address: '', phoneCountryCode: '55', phoneDDD: '' });

  // Paises com bandeira (flagcdn.com)
  const countries = [
    { code: '55', iso: 'br', name: 'Brasil' },
    { code: '33', iso: 'fr', name: 'França' },
    { code: '1', iso: 'us', name: 'EUA / Canadá' },
    { code: '351', iso: 'pt', name: 'Portugal' },
    { code: '34', iso: 'es', name: 'Espanha' },
    { code: '44', iso: 'gb', name: 'Reino Unido' },
    { code: '54', iso: 'ar', name: 'Argentina' },
    { code: '598', iso: 'uy', name: 'Uruguai' },
    { code: '595', iso: 'py', name: 'Paraguai' },
    { code: '56', iso: 'cl', name: 'Chile' },
    { code: '57', iso: 'co', name: 'Colômbia' },
    { code: '52', iso: 'mx', name: 'México' },
    { code: '49', iso: 'de', name: 'Alemanha' },
    { code: '39', iso: 'it', name: 'Itália' },
    { code: '41', iso: 'ch', name: 'Suíça' },
    { code: '32', iso: 'be', name: 'Bélgica' },
    { code: '31', iso: 'nl', name: 'Holanda' },
    { code: '81', iso: 'jp', name: 'Japão' },
    { code: '86', iso: 'cn', name: 'China' },
    { code: '91', iso: 'in', name: 'Índia' },
    { code: '61', iso: 'au', name: 'Austrália' },
    { code: '27', iso: 'za', name: 'África do Sul' },
    { code: '971', iso: 'ae', name: 'Emirados Árabes' },
    { code: '972', iso: 'il', name: 'Israel' },
    { code: '7', iso: 'ru', name: 'Rússia' },
  ];
  let showCountryDropdown = $state(false);
  let selectedCountry = $derived(countries.find(c => c.code === clientData.phoneCountryCode) || countries[0]);

  function selectCountry(code: string) {
    clientData.phoneCountryCode = code;
    clientData.phoneDDD = '';
    clientData.phone = '';
    showCountryDropdown = false;
  }

  // DDDs do Brasil por estado
  const brDDDs: { ddd: string; label: string }[] = [
    // Sudeste
    { ddd: '11', label: '11 - SP Capital' },
    { ddd: '12', label: '12 - SP Vale do Paraiba' },
    { ddd: '13', label: '13 - SP Litoral' },
    { ddd: '14', label: '14 - SP Bauru' },
    { ddd: '15', label: '15 - SP Sorocaba' },
    { ddd: '16', label: '16 - SP Ribeirao Preto' },
    { ddd: '17', label: '17 - SP S. J. Rio Preto' },
    { ddd: '18', label: '18 - SP Pres. Prudente' },
    { ddd: '19', label: '19 - SP Campinas' },
    { ddd: '21', label: '21 - RJ Capital' },
    { ddd: '22', label: '22 - RJ Interior' },
    { ddd: '24', label: '24 - RJ Volta Redonda' },
    { ddd: '27', label: '27 - ES Vitoria' },
    { ddd: '28', label: '28 - ES Sul' },
    { ddd: '31', label: '31 - MG BH' },
    { ddd: '32', label: '32 - MG Juiz de Fora' },
    { ddd: '33', label: '33 - MG Gov. Valadares' },
    { ddd: '34', label: '34 - MG Uberlandia' },
    { ddd: '35', label: '35 - MG Pocos de Caldas' },
    { ddd: '37', label: '37 - MG Divinopolis' },
    { ddd: '38', label: '38 - MG Montes Claros' },
    // Sul
    { ddd: '41', label: '41 - PR Curitiba' },
    { ddd: '42', label: '42 - PR Ponta Grossa' },
    { ddd: '43', label: '43 - PR Londrina' },
    { ddd: '44', label: '44 - PR Maringa' },
    { ddd: '45', label: '45 - PR Foz do Iguacu' },
    { ddd: '46', label: '46 - PR Pato Branco' },
    { ddd: '47', label: '47 - SC Joinville' },
    { ddd: '48', label: '48 - SC Florianopolis' },
    { ddd: '49', label: '49 - SC Chapeco' },
    { ddd: '51', label: '51 - RS Porto Alegre' },
    { ddd: '53', label: '53 - RS Pelotas' },
    { ddd: '54', label: '54 - RS Caxias do Sul' },
    { ddd: '55', label: '55 - RS Santa Maria' },
    // Centro-Oeste
    { ddd: '61', label: '61 - DF Brasilia' },
    { ddd: '62', label: '62 - GO Goiania' },
    { ddd: '63', label: '63 - TO Palmas' },
    { ddd: '64', label: '64 - GO Rio Verde' },
    { ddd: '65', label: '65 - MT Cuiaba' },
    { ddd: '66', label: '66 - MT Rondonopolis' },
    { ddd: '67', label: '67 - MS Campo Grande' },
    { ddd: '68', label: '68 - AC Rio Branco' },
    { ddd: '69', label: '69 - RO Porto Velho' },
    // Nordeste
    { ddd: '71', label: '71 - BA Salvador' },
    { ddd: '73', label: '73 - BA Ilheus' },
    { ddd: '74', label: '74 - BA Juazeiro' },
    { ddd: '75', label: '75 - BA Feira de Santana' },
    { ddd: '77', label: '77 - BA Vit. da Conquista' },
    { ddd: '79', label: '79 - SE Aracaju' },
    { ddd: '81', label: '81 - PE Recife' },
    { ddd: '82', label: '82 - AL Maceio' },
    { ddd: '83', label: '83 - PB Joao Pessoa' },
    { ddd: '84', label: '84 - RN Natal' },
    { ddd: '85', label: '85 - CE Fortaleza' },
    { ddd: '86', label: '86 - PI Teresina' },
    { ddd: '87', label: '87 - PE Petrolina' },
    { ddd: '88', label: '88 - CE Juazeiro do Norte' },
    { ddd: '89', label: '89 - PI Picos' },
    // Norte
    { ddd: '91', label: '91 - PA Belem' },
    { ddd: '92', label: '92 - AM Manaus' },
    { ddd: '93', label: '93 - PA Santarem' },
    { ddd: '94', label: '94 - PA Maraba' },
    { ddd: '95', label: '95 - RR Boa Vista' },
    { ddd: '96', label: '96 - AP Macapa' },
    { ddd: '97', label: '97 - AM Interior' },
    { ddd: '98', label: '98 - MA Sao Luis' },
    { ddd: '99', label: '99 - MA Imperatriz' },
  ];

  let emailValid = $derived(/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(clientData.email));
  let isBrazil = $derived(clientData.phoneCountryCode === '55');
  let phoneValid = $derived.by(() => {
    if (!clientData.phoneCountryCode) return false;
    if (isBrazil) {
      if (!clientData.phoneDDD) return false;
      const digits = clientData.phone.replace(/\D/g, '');
      return digits.length >= 8;
    }
    // Outros paises: DDD + numero com pelo menos 6 digitos
    const digits = clientData.phone.replace(/\D/g, '');
    return clientData.phoneDDD.trim().length > 0 && digits.length >= 5;
  });
  let currentNodeId = $state<string | null>(null);
  let answers = $state<{ node_id: string; question: string; value: string; label?: string }[]>([]);
  let endNode = $state<FlowNode | null>(null);
  let submitting = $state(false);
  let inputValue = $state('');

  // Scheduling state
  let schedulingStep = $state<'calendar' | 'time' | 'confirm' | 'done'>('calendar');
  let availableDates = $state<{ date: string; available: boolean; slots_count: number }[]>([]);
  let availableSlots = $state<string[]>([]);
  let selectedDate = $state('');
  let selectedTime = $state('');
  let calMonth = $state(new Date().getMonth());
  let calYear = $state(new Date().getFullYear());
  let loadingDates = $state(false);
  let loadingSlots = $state(false);
  let schedulingResult = $state<{ message: string; gcal_event_link?: string; whatsapp_sent?: boolean; email_sent?: boolean } | null>(null);

  let resultText = $state('');

  let currentNode = $derived(flow?.nodes.find(n => n.id === currentNodeId) || null);
  let totalQuestions = $derived(flow?.nodes.filter(n => n.type === 'question').length || 0);
  let answeredCount = $derived(answers.length);
  let progressPercent = $derived(totalQuestions > 0 ? Math.round((answeredCount / totalQuestions) * 100) : 0);

  onMount(async () => {
    try {
      const slug = page.params.slug;
      if (slug) {
        flow = await flowService.getBySlug(slug);
      }
      if (!flow) error = 'Questionnaire non trouve';
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }

    if (!(window as any).__utmTrackingInjected) {
      (window as any).__utmTrackingInjected = true;
      const s = document.createElement('script');
      s.textContent = utmTrackingScript;
      document.body.appendChild(s);
    }
  });

  async function startQuestions() {
    if (!clientData.name.trim() || !emailValid || !phoneValid) return;

    // Salvar lead no backend (MongoDB + ActiveCampaign) — fire and forget
    try {
      const localDigits = clientData.phone.replace(/\D/g, '');
      const ddd = clientData.phoneDDD.replace(/\D/g, '');
      const fullPhone = localDigits ? `${ddd}${localDigits}` : '';
      fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          flow_id: flow?._id || '',
          flow_slug: flow?.slug || '',
          client_name: clientData.name,
          client_email: clientData.email,
          client_phone: fullPhone || undefined,
          client_phone_country_code: fullPhone ? clientData.phoneCountryCode : undefined,
          client_address: clientData.address || undefined,
          activecampaign_list_id: flow?.activecampaign_list_id || undefined,
        })
      }).catch(() => {}); // nao bloqueia o fluxo
    } catch { /* silent */ }

    phase = 'questions';
    const startNode = flow!.nodes.find(n => n.type === 'start');
    if (!startNode) return;
    const edge = flow!.edges.find(e => e.source === startNode.id);
    if (edge) {
      currentNodeId = edge.target;
      processCurrentNode();
    }
  }

  function processCurrentNode() {
    if (!currentNode) return;
    if (currentNode.type === 'message') {
      setTimeout(() => {
        const edge = flow!.edges.find(e => e.source === currentNodeId);
        if (edge) {
          currentNodeId = edge.target;
          processCurrentNode();
        }
      }, 2500);
    } else if (currentNode.type === 'end') {
      endNode = currentNode;
      submitToBackend();
      if (currentNode.data.endType === 'scheduling') {
        phase = 'scheduling';
        schedulingStep = 'calendar';
        loadAvailableDates(calMonth + 1, calYear);
      } else {
        phase = 'end';
      }
    }
  }

  async function submitToBackend() {
    if (!flow || !endNode) return;
    submitting = true;
    resultText = '';

    try {
      const localDigits = clientData.phone.replace(/\D/g, '');
      const ddd = clientData.phoneDDD.replace(/\D/g, '');
      const fullPhone = localDigits ? `+${clientData.phoneCountryCode}${ddd}${localDigits}` : undefined;
      const payload = {
        flow_id: flow._id || '',
        flow_slug: flow.slug,
        client_name: clientData.name,
        client_email: clientData.email,
        client_phone: fullPhone,
        client_address: clientData.address || undefined,
        answers,
        end_node_id: endNode.id,
      };

      await submissionService.submit(payload);
      resultText = endNode.data.message || 'Obrigado pelas suas respostas!';
    } catch (e: any) {
      resultText = 'Erro ao enviar. Tente novamente.';
    } finally {
      submitting = false;
    }
  }

  function selectAnswer(value: string | number, handleId?: string, label?: string) {
    if (!currentNode) return;
    answers = [...answers, {
      node_id: currentNode.id,
      question: currentNode.data.title,
      value: String(value),
      label: label || String(value)
    }];
    let nextEdge: FlowEdge | undefined;
    if (handleId) {
      nextEdge = flow!.edges.find(e => e.source === currentNodeId && e.sourceHandle === handleId);
    }
    if (!nextEdge) {
      nextEdge = flow!.edges.find(e => e.source === currentNodeId && !e.sourceHandle);
    }
    if (!nextEdge) {
      nextEdge = flow!.edges.find(e => e.source === currentNodeId);
    }
    if (nextEdge) {
      currentNodeId = nextEdge.target;
      processCurrentNode();
    }
  }

  function goBack() {
    if (answers.length === 0) {
      phase = 'form';
      return;
    }
    const last = answers[answers.length - 1];
    answers = answers.slice(0, -1);
    currentNodeId = last.node_id;
    phase = 'questions';
    endNode = null;
  }

  // ── Scheduling functions ──────────────────────────────
  async function loadAvailableDates(month: number, year: number) {
    loadingDates = true;
    try {
      const res = await fetch(`/api/scheduling?action=dates&month=${month}&year=${year}`);
      if (res.ok) availableDates = await res.json();
    } catch (e) { /* silent */ }
    loadingDates = false;
  }

  async function selectDate(date: string) {
    selectedDate = date;
    selectedTime = '';
    loadingSlots = true;
    try {
      const res = await fetch(`/api/scheduling?action=slots&date=${date}`);
      if (res.ok) availableSlots = await res.json();
    } catch (e) { /* silent */ }
    loadingSlots = false;
    schedulingStep = 'time';
  }

  function selectTime(time: string) {
    selectedTime = time;
  }

  function confirmScheduling() {
    schedulingStep = 'confirm';
  }

  async function submitScheduling() {
    submitting = true;
    try {
      const res = await fetch('/api/scheduling', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          flow_id: flow?._id || '',
          flow_slug: flow?.slug || '',
          lead_name: clientData.name,
          lead_email: clientData.email,
          lead_phone: clientData.phone.replace(/\D/g, '') ? `+${clientData.phoneCountryCode}${clientData.phoneDDD.replace(/\D/g, '')}${clientData.phone.replace(/\D/g, '')}` : undefined,
          lead_address: clientData.address,
          qualifying_answers: answers,
          scheduled_date: selectedDate,
          scheduled_time: selectedTime,
          whatsapp_template: endNode?.data.whatsappTemplate || undefined,
          whatsapp_variables: endNode?.data.whatsappVariables || undefined,
        })
      });
      if (res.ok) {
        const data = await res.json();
        schedulingResult = data;
        schedulingStep = 'done';
      }
    } catch (e) { /* silent */ }
    submitting = false;
  }

  function prevCalMonth() {
    if (calMonth === 0) { calMonth = 11; calYear--; }
    else calMonth--;
    loadAvailableDates(calMonth + 1, calYear);
  }

  function nextCalMonth() {
    if (calMonth === 11) { calMonth = 0; calYear++; }
    else calMonth++;
    loadAvailableDates(calMonth + 1, calYear);
  }

  function formatDateBR(dateStr: string): string {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' });
  }

  const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];
  const monthNames = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

  let calDaysInMonth = $derived(new Date(calYear, calMonth + 1, 0).getDate());
  let calFirstDay = $derived(new Date(calYear, calMonth, 1).getDay());
  let dateMap = $derived.by(() => {
    const map: Record<string, { available: boolean; slots_count: number }> = {};
    for (const d of availableDates) map[d.date] = d;
    return map;
  });
  let canGoPrev = $derived.by(() => {
    const now = new Date();
    return calYear > now.getFullYear() || (calYear === now.getFullYear() && calMonth > now.getMonth());
  });
  let morningSlots = $derived(availableSlots.filter(s => parseInt(s.split(':')[0]) < 12));
  let afternoonSlots = $derived(availableSlots.filter(s => parseInt(s.split(':')[0]) >= 12));


</script>

<div class="min-h-screen flex items-center justify-center p-3 sm:p-4 md:p-6 relative overflow-hidden" style="font-weight: 400; background: #000000; --tc: {theme.main};">
  <div class="relative z-10 max-w-[460px] w-full text-base">

    {#if loading}
      <div class="bg-white/95 backdrop-blur-sm rounded-2xl sm:rounded-3xl border border-white/50 shadow-[0_20px_60px_rgba(15,10,26,0.35)] p-10 sm:p-16 text-center">
        <div class="w-10 h-10 border-[3px] border-t-transparent rounded-full animate-spin mx-auto mb-4" style="border-color: {theme.main}; border-top-color: transparent;"></div>
        <p class="text-sm text-gray-400">Carregando...</p>
      </div>

    {:else if error}
      <div class="bg-white/95 backdrop-blur-sm rounded-2xl sm:rounded-3xl border border-white/50 shadow-[0_20px_60px_rgba(15,10,26,0.35)] p-8 sm:p-12 text-center text-red-500 text-sm">{error}</div>

    {:else if phase === 'form'}
      <div class="bg-white/95 backdrop-blur-sm rounded-2xl sm:rounded-3xl border border-white/50 shadow-[0_24px_70px_rgba(15,10,26,0.4)] overflow-hidden">

        <!-- Header com cor do tema -->
        <div class="px-5 sm:px-8 pt-2 pb-1 text-center" style="background: {theme.gradientHeader};">
          <img src="https://br.itvalleyschool.com/wp-content/uploads/2024/06/logo_horizontal_mono_branca_1-1024x511.webp" alt="IT Valley School" class="h-20 sm:h-24 md:h-28 mx-auto mb-1 drop-shadow-[0_12px_30px_rgba(0,0,0,0.32)]" />
          <p class="text-[13px] sm:text-[15px] text-white/85 font-light tracking-[0.01em]">Preencha seus dados para falar com nosso consultor</p>
        </div>

        <!-- Campos -->
        <div class="px-4 sm:px-8 py-5 sm:py-8 space-y-4">

          <!-- Nome -->
          <div>
            <label for="form-field-name" class="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">Nome completo</label>
            <input id="form-field-name" type="text" bind:value={clientData.name} class="w-full border border-gray-200/90 bg-gray-50/70 rounded-xl px-4 py-3 text-[15px] text-gray-800 placeholder-gray-400 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 outline-none transition-all" placeholder="Seu nome completo" />
          </div>

          <!-- Email -->
          <div>
            <label for="form-field-email" class="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">E-mail</label>
            <input id="form-field-email" type="email" bind:value={clientData.email} class="w-full border border-gray-200/90 bg-gray-50/70 rounded-xl px-4 py-3 text-[15px] text-gray-800 placeholder-gray-400 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 outline-none transition-all" placeholder="seu@email.com" />
            {#if clientData.email && !emailValid}
              <p class="text-xs text-red-400 mt-1">Informe um e-mail válido</p>
            {/if}
          </div>

          <!-- WhatsApp -->
          <div>
            <label for="form-field-phone" class="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">WhatsApp</label>

            <!-- DDI - Dropdown customizado com bandeiras -->
            <div class="relative mb-2">
              <button
                type="button"
                onclick={() => showCountryDropdown = !showCountryDropdown}
                class="w-full border border-gray-200/90 bg-gray-50/70 rounded-xl px-4 py-3 text-sm text-gray-800 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 outline-none transition-all cursor-pointer flex items-center gap-3"
              >
                <img src="https://flagcdn.com/24x18/{selectedCountry.iso}.png" alt={selectedCountry.name} class="w-6 h-[18px] rounded-sm object-cover" />
                <span class="flex-1 text-left">{selectedCountry.name} (+{selectedCountry.code})</span>
                <svg class="w-4 h-4 text-gray-400 transition-transform {showCountryDropdown ? 'rotate-180' : ''}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
              </button>

              {#if showCountryDropdown}
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div class="absolute inset-0 fixed z-20" onclick={() => showCountryDropdown = false} onkeydown={() => {}}></div>
                <div class="absolute z-30 top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                  {#each countries as country}
                    <button
                      type="button"
                      onclick={() => selectCountry(country.code)}
                      class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors cursor-pointer {country.code === clientData.phoneCountryCode ? 'bg-gray-100 font-medium' : ''}"
                    >
                      <img src="https://flagcdn.com/24x18/{country.iso}.png" alt={country.name} class="w-6 h-[18px] rounded-sm object-cover" />
                      <span class="flex-1 text-left">{country.name}</span>
                      <span class="text-gray-400 text-xs">+{country.code}</span>
                    </button>
                  {/each}
                </div>
              {/if}
            </div>

            <!-- DDD + Numero -->
            <div class="flex flex-col sm:flex-row gap-2">
              {#if isBrazil}
                <select
                  id="client-ddd"
                  bind:value={clientData.phoneDDD}
                  class="border border-gray-200/90 bg-gray-50/70 rounded-xl px-3 py-3 text-sm text-gray-800 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 outline-none transition-all w-full sm:min-w-[145px] sm:w-auto cursor-pointer"
                >
                  <option value="" disabled>DDD</option>
                  {#each brDDDs as item}
                    <option value={item.ddd}>{item.label}</option>
                  {/each}
                </select>
              {:else}
                <input
                  id="client-area-code"
                  type="text"
                  bind:value={clientData.phoneDDD}
                  placeholder="Cód. área"
                  oninput={(e) => {
                    const input = e.target as HTMLInputElement;
                    clientData.phoneDDD = input.value.replace(/\D/g, '').slice(0, 5);
                  }}
                  class="border border-gray-200/90 bg-gray-50/70 rounded-xl px-4 py-3 text-sm text-gray-800 placeholder-gray-400 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 outline-none transition-all w-full sm:w-[110px]"
                />
              {/if}

              <input
                id="form-field-phone"
                type="tel"
                bind:value={clientData.phone}
                placeholder={isBrazil ? '99999-9999' : 'Número'}
                oninput={(e) => {
                  const input = e.target as HTMLInputElement;
                  if (isBrazil) {
                    let v = input.value.replace(/\D/g, '').slice(0, 9);
                    if (v.length > 5) v = `${v.slice(0,5)}-${v.slice(5)}`;
                    clientData.phone = v;
                  }
                }}
                class="flex-1 border border-gray-200/90 bg-gray-50/70 rounded-xl px-4 py-3 text-[15px] text-gray-800 placeholder-gray-400 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 outline-none transition-all"
              />
            </div>

            {#if clientData.phoneDDD && clientData.phone}
              <p class="text-[11px] text-gray-400 mt-1.5 font-mono">
                +{clientData.phoneCountryCode} ({clientData.phoneDDD}) {clientData.phone}
              </p>
            {/if}

            {#if !phoneValid && (clientData.phone || clientData.phoneDDD)}
              <p class="text-xs text-red-400 mt-1">
                {#if isBrazil && !clientData.phoneDDD}
                  Selecione o DDD
                {:else if !isBrazil && !clientData.phoneDDD.trim()}
                  Informe o código de área
                {:else}
                  Número incompleto
                {/if}
              </p>
            {/if}
          </div>

          <!-- Botao -->
          <button
            onclick={startQuestions}
            disabled={!clientData.name.trim() || !emailValid || !phoneValid}
            class="w-full py-3.5 rounded-xl text-[15px] font-semibold text-white disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition-all duration-200 active:scale-[0.99] mt-2"
            style="background: {theme.gradient};"
          >
            Começar
          </button>

          <p class="text-center text-[12px] sm:text-[13px] text-gray-500 mt-3 tracking-wide font-medium">Powered by IT Valley School</p>
        </div>
      </div>

    {:else if phase === 'questions' && currentNode}
      <div class="bg-white/95 backdrop-blur-sm rounded-2xl sm:rounded-3xl border border-white/50 shadow-[0_20px_60px_rgba(15,10,26,0.35)] overflow-hidden">
      <!-- Progress -->
      <div class="bg-gray-100/80 px-4 sm:px-6 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-200/80">
        <span class="text-sm font-medium text-gray-500">Pergunta {answeredCount + 1} / {totalQuestions}</span>
        <div class="flex items-center gap-2">
          <div class="w-28 bg-gray-200 rounded-full h-2">
            <div class="h-2 rounded-full transition-all duration-300" style="width: {progressPercent}%; background: {theme.gradient}"></div>
          </div>
          <span class="text-sm text-gray-500">{progressPercent}%</span>
        </div>
      </div>

      <div class="p-5 sm:p-8">
        {#if currentNode.type === 'message'}
          <div class="text-center py-6">
            <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background: color-mix(in srgb, var(--tc) 15%, transparent); mx-auto mb-4">
              <svg class="w-6 h-6 transition-colors" style="color: var(--tc);" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-800 mb-3">{currentNode.data.title}</h3>
            <p class="text-base text-gray-500">{currentNode.data.message}</p>
          </div>
        {:else}
          <h3 class="text-xl font-semibold text-gray-800 mb-2">{currentNode.data.title}</h3>

          {#if currentNode.data.tooltip}
            <p class="text-sm text-gray-500 mb-5">{currentNode.data.tooltip}</p>
          {:else}
            <div class="mb-5"></div>
          {/if}

          {#if currentNode.data.questionType === 'single_choice' && currentNode.data.options}
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {#each currentNode.data.options as opt}
                <button
                  onclick={() => selectAnswer(opt.value, opt.id, opt.label)}
                  class="border-2 border-gray-200 rounded-xl px-4 py-4 text-center text-base font-medium text-gray-700 hover:border-violet-500/50 hover:bg-violet-50 hover:text-gray-900 transition-all cursor-pointer"
                >
                  {opt.label}
                </button>
              {/each}
            </div>
          {:else if currentNode.data.questionType === 'yes_no'}
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                onclick={() => selectAnswer('Oui', 'yes')}
                class="border-2 border-gray-200 rounded-xl px-4 py-5 text-center text-lg font-medium text-gray-700 hover:border-violet-500/50 hover:bg-violet-50 hover:text-gray-900 transition-all cursor-pointer"
              >
                Sim
              </button>
              <button
                onclick={() => selectAnswer('Non', 'no')}
                class="border-2 border-gray-200 rounded-xl px-4 py-5 text-center text-lg font-medium text-gray-700 hover:border-red-500/50 hover:bg-red-50 hover:text-gray-900 transition-all cursor-pointer"
              >
                Não
              </button>
            </div>
          {:else if currentNode.data.questionType === 'number'}
            <div class="flex flex-col sm:flex-row gap-2">
              <input
                type="number"
                bind:value={inputValue}
                class="flex-1 bg-gray-50/70 border border-gray-200/90 rounded-xl px-4 py-3 text-base text-gray-800 placeholder-gray-400 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 outline-none"
                placeholder="Digite um número"
              />
              <button
                onclick={() => { selectAnswer(inputValue); inputValue = ''; }}
                disabled={!inputValue}
                class="w-full sm:w-auto px-6 py-3 rounded-xl text-base font-medium text-white disabled:opacity-40 cursor-pointer transition-colors"
                style="background: {theme.gradient};"
              >
                Próximo
              </button>
            </div>
          {:else}
            <div class="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                bind:value={inputValue}
                class="flex-1 bg-gray-50/70 border border-gray-200/90 rounded-xl px-4 py-3 text-base text-gray-800 placeholder-gray-400 focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 outline-none"
                placeholder="Sua resposta"
              />
              <button
                onclick={() => { selectAnswer(inputValue); inputValue = ''; }}
                disabled={!inputValue.trim()}
                class="w-full sm:w-auto px-6 py-3 rounded-xl text-base font-medium text-white disabled:opacity-40 cursor-pointer transition-colors"
                style="background: {theme.gradient};"
              >
                Próximo
              </button>
            </div>
          {/if}
        {/if}

        <button
          onclick={goBack}
          class="mt-6 text-sm text-gray-500 hover:text-gray-700 cursor-pointer transition-colors flex items-center gap-1.5"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          Voltar
        </button>
      </div>
      </div>

    {:else if phase === 'end' && endNode}
      <div class="bg-white/95 backdrop-blur-sm rounded-2xl sm:rounded-3xl border border-white/50 shadow-[0_20px_60px_rgba(15,10,26,0.35)] overflow-hidden">
      {#if submitting}
        <div class="p-5 sm:p-8">
          <div class="text-center py-8">
            <div class="w-12 h-12 border-3 border-t-transparent" style="border-color: var(--tc); border-top-color: transparent; rounded-full animate-spin mx-auto mb-5"></div>
            <p class="text-base text-gray-800 font-semibold">Processando suas respostas...</p>
            <p class="text-sm text-gray-500 mt-2">Aguarde um momento</p>
          </div>
        </div>

      {:else}
        <div class="p-5 sm:p-8 text-center">
          <div class="w-14 h-14 rounded-full flex items-center justify-center" style="background: color-mix(in srgb, var(--tc) 15%, transparent); mx-auto mb-3">
            <svg class="w-7 h-7 transition-colors" style="color: var(--tc);" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-800 mb-2">{endNode.data.title}</h3>
          <p class="text-sm text-gray-500">{resultText}</p>
        </div>
      {/if}
      </div>

    <!-- ==================== SCHEDULING ==================== -->
    {:else if phase === 'scheduling'}
      <div class="bg-white/95 backdrop-blur-sm rounded-2xl sm:rounded-3xl border border-white/50 shadow-[0_20px_60px_rgba(15,10,26,0.35)] overflow-hidden">

      {#if schedulingStep === 'calendar'}
        <div class="p-4 sm:p-6">
          <div class="text-center mb-5">
            <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background: color-mix(in srgb, var(--tc) 15%, transparent); mx-auto mb-3">
              <svg class="w-6 h-6 transition-colors" style="color: var(--tc);" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-800">Escolha o dia</h3>
            <p class="text-sm text-gray-500">{endNode?.data.message || 'Selecione uma data disponível'}</p>
          </div>

          <!-- Calendar -->
          <div class="border border-gray-200 rounded-xl overflow-hidden">
            <!-- Month nav -->
            <div class="flex items-center justify-between px-3 sm:px-4 py-2.5 sm:py-3 bg-gray-50 border-b border-gray-200">
              <button onclick={prevCalMonth} disabled={!canGoPrev} aria-label="Mês anterior" class="p-1.5 rounded-lg hover:bg-gray-200 disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer transition-colors">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
              </button>
              <span class="text-xs sm:text-sm font-semibold text-gray-800">{monthNames[calMonth]} {calYear}</span>
              <button onclick={nextCalMonth} aria-label="Próximo mês" class="p-1.5 rounded-lg hover:bg-gray-200 cursor-pointer transition-colors">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
              </button>
            </div>

            <!-- Weekday headers -->
            <div class="grid grid-cols-7 border-b border-gray-200">
              {#each weekdays as wd}
                <div class="py-2 text-center text-[9px] sm:text-[10px] font-semibold text-gray-500 uppercase">{wd}</div>
              {/each}
            </div>

            <!-- Days -->
            {#if loadingDates}
              <div class="py-12 text-center">
                <div class="w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
            {:else}
              <div class="grid grid-cols-7 gap-px p-2">
                {#each Array(calFirstDay) as _}<div></div>{/each}
                {#each Array(calDaysInMonth) as _, i}
                  {@const day = i + 1}
                  {@const dateStr = `${calYear}-${String(calMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`}
                  {@const info = dateMap[dateStr]}
                  {@const avail = info?.available ?? false}
                  {@const isToday = new Date().toISOString().slice(0, 10) === dateStr}
                  <button
                    onclick={() => avail && selectDate(dateStr)}
                    disabled={!avail}
                    class="relative aspect-square flex items-center justify-center rounded-lg text-xs sm:text-sm font-medium transition-all
                    {selectedDate === dateStr
                      ? 'text-white shadow-md scale-110" style="background: var(--tc);'
                      : avail
                        ? 'text-gray-700 hover:bg-violet-500/10 hover:text-violet-600 cursor-pointer'
                        : 'text-gray-300 cursor-not-allowed'}"
                  >
                    {day}
                    {#if isToday && selectedDate !== dateStr}
                      <span class="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-blue-500"></span>
                    {/if}
                  </button>
                {/each}
              </div>
            {/if}
          </div>

          <button onclick={goBack} class="mt-4 text-xs text-gray-400 hover:text-gray-600 cursor-pointer transition-colors flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
            Voltar
          </button>
        </div>

      {:else if schedulingStep === 'time'}
        <div class="p-4 sm:p-6">
          <div class="text-center mb-5">
            <h3 class="text-lg font-bold text-gray-800">Escolha o horário</h3>
            <p class="text-sm text-gray-500 capitalize">{formatDateBR(selectedDate)}</p>
          </div>

          {#if loadingSlots}
            <div class="py-12 text-center">
              <div class="w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          {:else}
            <!-- Morning -->
            {#if morningSlots.length > 0}
              <div class="mb-4">
                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Manhã</p>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {#each morningSlots as slot}
                    <button
                      onclick={() => selectTime(slot)}
                      class="py-2.5 rounded-xl border-2 text-sm font-semibold transition-all cursor-pointer
                      {selectedTime === slot ? 'text-white" style="border-color: var(--tc); background: color-mix(in srgb, var(--tc) 15%, transparent); color: var(--tc);' : 'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50'}"
                    >{slot}</button>
                  {/each}
                </div>
              </div>
            {/if}
            <!-- Afternoon -->
            {#if afternoonSlots.length > 0}
              <div class="mb-4">
                <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Tarde</p>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {#each afternoonSlots as slot}
                    <button
                      onclick={() => selectTime(slot)}
                      class="py-2.5 rounded-xl border-2 text-sm font-semibold transition-all cursor-pointer
                      {selectedTime === slot ? 'text-white" style="border-color: var(--tc); background: color-mix(in srgb, var(--tc) 15%, transparent); color: var(--tc);' : 'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50'}"
                    >{slot}</button>
                  {/each}
                </div>
              </div>
            {/if}
            {#if availableSlots.length === 0}
              <p class="text-center text-gray-500 py-8">Nenhum horário disponível nesta data</p>
            {/if}
          {/if}

          {#if selectedTime}
            <button
              onclick={confirmScheduling}
              class="w-full py-3 rounded-lg text-sm font-semibold text-white cursor-pointer transition-colors mt-2" style="background: {theme.gradient};"
            >
              Continuar
            </button>
          {/if}

          <button onclick={() => { schedulingStep = 'calendar'; selectedTime = ''; }} class="mt-3 text-xs text-gray-400 hover:text-gray-600 cursor-pointer transition-colors flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
            Voltar ao calendário
          </button>
        </div>

      {:else if schedulingStep === 'confirm'}
        <div class="p-4 sm:p-6">
          <div class="text-center mb-5">
            <h3 class="text-lg font-bold text-gray-800">Confirme seu agendamento</h3>
            <p class="text-sm text-gray-500">Verifique os dados antes de confirmar</p>
          </div>

          <div class="bg-gray-50 rounded-xl p-4 sm:p-5 space-y-3 mb-5 border border-gray-200">
            <div class="flex flex-col sm:flex-row sm:justify-between gap-1"><span class="text-xs text-gray-500">Nome</span><span class="text-sm font-medium text-gray-800 break-words sm:text-right">{clientData.name}</span></div>
            <div class="flex flex-col sm:flex-row sm:justify-between gap-1"><span class="text-xs text-gray-500">E-mail</span><span class="text-sm font-medium text-gray-800 break-all sm:text-right">{clientData.email}</span></div>
            {#if clientData.phone}
              <div class="flex flex-col sm:flex-row sm:justify-between gap-1"><span class="text-xs text-gray-500">Telefone</span><span class="text-sm font-medium text-gray-800 break-words sm:text-right">+{clientData.phoneCountryCode} ({clientData.phoneDDD}) {clientData.phone}</span></div>
            {/if}
            <hr class="border-gray-200" />
            <div class="flex flex-col sm:flex-row sm:justify-between gap-1"><span class="text-xs text-gray-500">Data</span><span class="text-sm font-medium text-gray-800 capitalize sm:text-right">{formatDateBR(selectedDate)}</span></div>
            <div class="flex flex-col sm:flex-row sm:justify-between gap-1"><span class="text-xs text-gray-500">Horario</span><span class="text-sm font-medium text-gray-800 sm:text-right">{selectedTime}</span></div>
          </div>

          <button
            onclick={submitScheduling}
            disabled={submitting}
            class="w-full py-3 rounded-lg text-sm font-semibold text-white disabled:opacity-50 cursor-pointer transition-colors" style="background: {theme.gradient};"
          >
            {#if submitting}
              <span class="inline-flex items-center gap-2">
                <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Agendando...
              </span>
            {:else}
              Confirmar Agendamento
            {/if}
          </button>

          <button onclick={() => schedulingStep = 'time'} class="mt-3 text-xs text-gray-400 hover:text-gray-600 cursor-pointer transition-colors flex items-center gap-1 mx-auto">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
            Voltar
          </button>
        </div>

      {:else if schedulingStep === 'done'}
        <div class="p-5 sm:p-8 text-center">
          <div class="w-16 h-16 rounded-full flex items-center justify-center" style="background: color-mix(in srgb, var(--tc) 15%, transparent); mx-auto mb-4">
            <svg class="w-8 h-8 transition-colors" style="color: var(--tc);" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">Agendamento Confirmado!</h3>
          <p class="text-sm text-gray-500 mb-4">{schedulingResult?.message || 'Você receberá uma confirmação em breve.'}</p>

          <div class="border" style="background: color-mix(in srgb, var(--tc) 10%, transparent); border-color: color-mix(in srgb, var(--tc) 20%, transparent); rounded-xl p-4 text-left space-y-2 mb-4">
            <div class="flex flex-col sm:flex-row sm:justify-between gap-1">
              <span class="text-xs" style="color: var(--tc);">Data</span>
              <span class="text-sm font-semibold text-gray-800 capitalize sm:text-right">{formatDateBR(selectedDate)}</span>
            </div>
            <div class="flex flex-col sm:flex-row sm:justify-between gap-1">
              <span class="text-xs" style="color: var(--tc);">Horario</span>
              <span class="text-sm font-semibold text-gray-800 sm:text-right">{selectedTime}</span>
            </div>
          </div>

          <!-- Notificacoes enviadas -->
          <div class="space-y-2 mb-4 text-left">
            {#if schedulingResult?.gcal_event_link}
              <div class="flex items-center gap-2 border" style="background: color-mix(in srgb, var(--tc) 10%, transparent); border-color: color-mix(in srgb, var(--tc) 20%, transparent); rounded-lg px-3 py-2">
                <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                </svg>
                <span class="text-xs" style="color: var(--tc);">Convite enviado para <strong>{clientData.email}</strong> via Google Calendar</span>
              </div>
            {/if}
            {#if schedulingResult?.email_sent}
              <div class="flex items-center gap-2 border" style="background: color-mix(in srgb, var(--tc) 10%, transparent); border-color: color-mix(in srgb, var(--tc) 20%, transparent); rounded-lg px-3 py-2">
                <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                </svg>
                <span class="text-xs" style="color: var(--tc);">E-mail enviado para <strong>{clientData.email}</strong></span>
              </div>
            {/if}
            {#if schedulingResult?.whatsapp_sent}
              <div class="flex items-center gap-2 border" style="background: color-mix(in srgb, var(--tc) 10%, transparent); border-color: color-mix(in srgb, var(--tc) 20%, transparent); rounded-lg px-3 py-2">
                <svg class="w-4 h-4 text-green-600 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
                  <path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.75.75 0 00.917.918l4.462-1.494A11.943 11.943 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-2.337 0-4.542-.664-6.407-1.813l-.456-.276-2.653.888.889-2.651-.277-.458A9.953 9.953 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/>
                </svg>
                <span class="text-xs" style="color: var(--tc);">WhatsApp enviado para <strong>+{clientData.phoneCountryCode} ({clientData.phoneDDD}) {clientData.phone}</strong></span>
              </div>
            {/if}
          </div>

          <p class="text-xs text-gray-500">Obrigado, {clientData.name}!</p>
        </div>
      {/if}
      </div>

    {/if}
  </div>
</div>
