<script lang="ts">
  import { goto } from '$app/navigation';
  let lang = $state<'pt' | 'fr' | 'en' | 'es'>('pt');
  let expandedFaq = $state<number | null>(null);
  function toggleFaq(i: number) { expandedFaq = expandedFaq === i ? null : i; }

  const i: Record<string, Record<string, string>> = {
    back: { pt: 'Voltar ao painel', fr: 'Retour au panneau', en: 'Back to dashboard', es: 'Volver al panel' },
    hero1: { pt: 'Bem-vindo ao Modo Agendamento!', fr: 'Bienvenue au Mode Rendez-vous !', en: 'Welcome to Scheduling Mode!', es: '¡Bienvenido al Modo Agendamiento!' },
    hero2: { pt: 'Transforme visitantes em reuniões agendadas — automaticamente.', fr: 'Transformez les visiteurs en réunions planifiées — automatiquement.', en: 'Turn visitors into booked meetings — automatically.', es: 'Transforme visitantes en reuniones agendadas — automáticamente.' },
    hero3: { pt: 'Sem troca de mensagens. Sem "quando você pode?". Só clica e agenda.', fr: 'Sans échange de messages. Sans "quand pouvez-vous ?". Cliquez et réservez.', en: 'No back-and-forth messaging. No "when can you?". Just click and book.', es: 'Sin intercambio de mensajes. Sin "¿cuándo puede?". Solo clic y agenda.' },

    whatTitle: { pt: 'O que é o Modo Agendamento?', fr: 'Qu\'est-ce que le Mode Rendez-vous ?', en: 'What is Scheduling Mode?', es: '¿Qué es el Modo Agendamiento?' },
    whatP1: { pt: 'Sabe quando alguém vê seu post no Instagram, manda mensagem pedindo informações, e vocês ficam trocando mensagens por horas até encontrar um horário livre? O Modo Agendamento resolve isso.', fr: 'Vous savez quand quelqu\'un voit votre post Instagram, envoie un message pour des informations, et vous échangez pendant des heures pour trouver un créneau libre ? Le Mode Rendez-vous résout cela.', en: 'You know when someone sees your Instagram post, sends a DM asking for info, and you spend hours going back and forth to find a free time? Scheduling Mode fixes this.', es: '¿Sabe cuando alguien ve su post en Instagram, manda mensaje pidiendo información, y quedan intercambiando mensajes por horas hasta encontrar un horario libre? El Modo Agendamiento resuelve esto.' },
    whatP2: { pt: 'O lead clica no seu link, responde perguntas rápidas de qualificação, escolhe dia e hora no calendário, e pronto — a reunião aparece no seu Google Calendar com todos os dados do lead.', fr: 'Le lead clique sur votre lien, répond à des questions rapides de qualification, choisit jour et heure sur le calendrier, et voilà — la réunion apparaît dans votre Google Calendar avec toutes les données du lead.', en: 'The lead clicks your link, answers quick qualifying questions, picks day and time on the calendar, and done — the meeting appears in your Google Calendar with all the lead\'s data.', es: 'El lead hace clic en su enlace, responde preguntas rápidas de calificación, elige día y hora en el calendario, y listo — la reunión aparece en su Google Calendar con todos los datos del lead.' },

    journeyTitle: { pt: 'A Jornada do Lead (o que ele vê)', fr: 'Le Parcours du Lead (ce qu\'il voit)', en: 'The Lead Journey (what they see)', es: 'La Jornada del Lead (lo que ve)' },

    guideTitle: { pt: 'Passo a Passo: Criando seu Primeiro Agendamento', fr: 'Étape par Étape : Créer Votre Premier RDV', en: 'Step by Step: Creating Your First Booking', es: 'Paso a Paso: Creando su Primer Agendamiento' },
    step1t: { pt: 'Passo 1: Clique em "Modo Agendamento" na home', fr: 'Étape 1 : Cliquez sur "Mode Rendez-vous" sur l\'accueil', en: 'Step 1: Click "Scheduling Mode" on the home page', es: 'Paso 1: Haga clic en "Modo Agendamiento" en la home' },
    step1d: { pt: 'Na página inicial do FlowQuote, clique no botão verde. Isso cria um fluxo pronto com perguntas de exemplo. Você vai direto pro dashboard de agendamentos.', fr: 'Sur la page d\'accueil de FlowQuote, cliquez sur le bouton vert. Cela crée un flux prêt avec des questions d\'exemple. Vous allez directement au tableau de bord.', en: 'On the FlowQuote home page, click the green button. This creates a ready flow with sample questions. You go straight to the scheduling dashboard.', es: 'En la página de inicio de FlowQuote, haga clic en el botón verde. Esto crea un flujo listo con preguntas de ejemplo. Va directo al dashboard de agendamientos.' },
    step2t: { pt: 'Passo 2: Edite as perguntas no editor visual', fr: 'Étape 2 : Éditez les questions dans l\'éditeur visuel', en: 'Step 2: Edit the questions in the visual editor', es: 'Paso 2: Edite las preguntas en el editor visual' },
    step2d: { pt: 'Clique em "Editar" no fluxo criado. Altere, adicione ou remova perguntas conforme o que você quer saber do lead antes de agendar.', fr: 'Cliquez sur "Éditer" dans le flux créé. Modifiez, ajoutez ou supprimez des questions selon ce que vous voulez savoir du lead avant de planifier.', en: 'Click "Edit" on the created flow. Modify, add or remove questions based on what you want to know about the lead before scheduling.', es: 'Haga clic en "Editar" en el flujo creado. Modifique, agregue o elimine preguntas según lo que quiera saber del lead antes de agendar.' },
    step3t: { pt: 'Passo 3: O nó final DEVE ser "Agendamento"', fr: 'Étape 3 : Le nœud final DOIT être "Rendez-vous"', en: 'Step 3: The end node MUST be "Scheduling"', es: 'Paso 3: El nodo final DEBE ser "Agendamiento"' },
    step3d: { pt: 'Clique no nó final roxo e verifique se o tipo está como "Agendamento (Calendário)". É isso que ativa o calendário para o lead.', fr: 'Cliquez sur le nœud final violet et vérifiez que le type est "Rendez-vous (Calendrier)". C\'est ce qui active le calendrier pour le lead.', en: 'Click the purple end node and verify the type is "Scheduling (Calendar)". This is what activates the calendar for the lead.', es: 'Haga clic en el nodo final morado y verifique que el tipo sea "Agendamiento (Calendario)". Esto es lo que activa el calendario para el lead.' },
    step4t: { pt: 'Passo 4: Publique e compartilhe o link!', fr: 'Étape 4 : Publiez et partagez le lien !', en: 'Step 4: Publish and share the link!', es: 'Paso 4: ¡Publique y comparta el enlace!' },
    step4d: { pt: 'Salve, publique e copie o link. Cole no Instagram, WhatsApp, site, onde quiser. Pronto!', fr: 'Enregistrez, publiez et copiez le lien. Collez sur Instagram, WhatsApp, site, où vous voulez. C\'est prêt !', en: 'Save, publish and copy the link. Paste on Instagram, WhatsApp, website, wherever. Done!', es: '¡Guarde, publique y copie el enlace. Pegue en Instagram, WhatsApp, sitio web, donde quiera. ¡Listo!' },

    dashTitle: { pt: 'Seu Painel de Controle', fr: 'Votre Tableau de Bord', en: 'Your Control Panel', es: 'Su Panel de Control' },
    dashP: { pt: 'No painel de agendamentos você tem duas abas:', fr: 'Dans le panneau de rendez-vous, vous avez deux onglets :', en: 'In the scheduling panel you have two tabs:', es: 'En el panel de agendamientos tiene dos pestañas:' },
    dashTab1: { pt: 'Fluxos — seus questionários de agendamento', fr: 'Flux — vos questionnaires de rendez-vous', en: 'Flows — your scheduling questionnaires', es: 'Flujos — sus cuestionarios de agendamiento' },
    dashTab2: { pt: 'Reservas — todos os agendamentos feitos (nome, data, hora, status)', fr: 'Réservations — tous les rendez-vous pris (nom, date, heure, statut)', en: 'Bookings — all appointments made (name, date, time, status)', es: 'Reservas — todos los agendamientos hechos (nombre, fecha, hora, estado)' },

    faqTitle: { pt: 'Perguntas Frequentes', fr: 'Questions Fréquentes', en: 'FAQ', es: 'Preguntas Frecuentes' },
    faq1q: { pt: 'De onde vêm os horários disponíveis?', fr: 'D\'où viennent les créneaux disponibles ?', en: 'Where do the available times come from?', es: '¿De dónde vienen los horarios disponibles?' },
    faq1a: { pt: 'Direto do seu Google Calendar! Se alguém já marcou às 10h, esse horário desaparece automaticamente pra todo mundo. Tudo em tempo real.', fr: 'Directement de votre Google Calendar ! Si quelqu\'un a déjà réservé à 10h, ce créneau disparaît automatiquement. Tout en temps réel.', en: 'Straight from your Google Calendar! If someone already booked 10 AM, that slot automatically disappears for everyone. All in real-time.', es: '¡Directo de su Google Calendar! Si alguien ya agendó a las 10h, ese horario desaparece automáticamente. Todo en tiempo real.' },
    faq2q: { pt: 'O lead recebe confirmação?', fr: 'Le lead reçoit une confirmation ?', en: 'Does the lead get a confirmation?', es: '¿El lead recibe confirmación?' },
    faq2a: { pt: 'Sim! Um evento é criado no Google Calendar e o lead é adicionado como participante — ele recebe o convite por email automaticamente.', fr: 'Oui ! Un événement est créé dans Google Calendar et le lead est ajouté comme participant — il reçoit l\'invitation par email automatiquement.', en: 'Yes! An event is created in Google Calendar and the lead is added as an attendee — they receive the invite by email automatically.', es: '¡Sí! Un evento se crea en Google Calendar y el lead es agregado como participante — recibe la invitación por email automáticamente.' },
    faq3q: { pt: 'Preciso vincular perguntas ao CSV como no orçamento?', fr: 'Dois-je lier les questions au CSV comme pour les devis ?', en: 'Do I need to link questions to CSV like in quotes?', es: '¿Necesito vincular preguntas al CSV como en presupuestos?' },
    faq3a: { pt: 'NÃO! No agendamento, todas as perguntas são de contexto/qualificação. Não há CSV, não há cálculo de preço. As perguntas servem apenas para você conhecer melhor o lead antes da reunião.', fr: 'NON ! Pour les rendez-vous, toutes les questions sont de contexte/qualification. Pas de CSV, pas de calcul de prix. Les questions servent uniquement à mieux connaître le lead avant la réunion.', en: 'NO! In scheduling, all questions are for context/qualification. No CSV, no price calculation. Questions only serve to better know the lead before the meeting.', es: '¡NO! En agendamiento, todas las preguntas son de contexto/calificación. No hay CSV, no hay cálculo de precio. Las preguntas sirven solo para conocer mejor al lead antes de la reunión.' },

    cta: { pt: 'Ir para Agendamentos', fr: 'Aller aux Rendez-vous', en: 'Go to Scheduling', es: 'Ir a Agendamientos' },
  };
  function _(k: string): string { return i[k]?.[lang] || i[k]?.['pt'] || k; }
</script>

<div class="min-h-screen bg-white">
  <header class="bg-white/80 backdrop-blur-md border-b sticky top-0 z-10">
    <div class="max-w-3xl mx-auto px-6 py-3 flex items-center justify-between">
      <button onclick={() => goto('/admin/scheduling')} class="text-sm text-gray-500 hover:text-gray-800 cursor-pointer flex items-center gap-1.5">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" /></svg>
        {_('back')}
      </button>
      <div class="flex gap-0.5 bg-gray-100 rounded-full p-0.5">
        {#each (['pt', 'fr', 'en', 'es'] as const) as l}
          <button onclick={() => lang = l} class="w-9 h-8 rounded-full text-xs font-bold uppercase cursor-pointer transition-all {lang === l ? 'bg-white text-green-600 shadow-sm' : 'text-gray-400 hover:text-gray-600'}">{l}</button>
        {/each}
      </div>
    </div>
  </header>

  <main class="max-w-3xl mx-auto px-6">

    <!-- HERO -->
    <section class="py-16 text-center">
      <div class="w-20 h-20 rounded-3xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-green-500/30">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5m-9-6h.008v.008H12v-.008zM12 15h.008v.008H12V15zm0 2.25h.008v.008H12v-.008zM9.75 15h.008v.008H9.75V15zm0 2.25h.008v.008H9.75v-.008zM7.5 15h.008v.008H7.5V15zm0 2.25h.008v.008H7.5v-.008zm6.75-4.5h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V15zm0 2.25h.008v.008h-.008v-.008zm2.25-4.5h.008v.008H16.5v-.008zm0 2.25h.008v.008H16.5V15z" /></svg>
      </div>
      <h1 class="text-4xl font-black text-gray-900 mb-3">{_('hero1')}</h1>
      <p class="text-lg text-gray-600 mb-2">{_('hero2')}</p>
      <p class="text-base text-gray-400">{_('hero3')}</p>
    </section>

    <!-- O QUE É -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-green-600 uppercase tracking-widest mb-2">01</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-4">{_('whatTitle')}</h3>
      <div class="bg-green-50 rounded-2xl p-6 space-y-4">
        <p class="text-gray-700 leading-relaxed">{_('whatP1')}</p>
        <p class="text-gray-600 leading-relaxed">{_('whatP2')}</p>
      </div>
    </section>

    <!-- JORNADA DO LEAD -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-green-600 uppercase tracking-widest mb-2">02</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-6">{_('journeyTitle')}</h3>

      <!-- Mockup: each step the lead sees -->
      <div class="space-y-6">
        <!-- Step A: Form -->
        <div class="border-2 border-gray-200 rounded-2xl overflow-hidden shadow-lg">
          <div class="bg-gray-100 px-4 py-2 flex items-center gap-2 border-b">
            <div class="flex gap-1.5"><div class="w-3 h-3 rounded-full bg-red-400"></div><div class="w-3 h-3 rounded-full bg-yellow-400"></div><div class="w-3 h-3 rounded-full bg-green-400"></div></div>
            <div class="flex-1 text-center text-xs text-gray-400">seusite.com/q/agendamento</div>
          </div>
          <div class="bg-gradient-to-b from-gray-50 to-gray-100 p-6 flex justify-center">
            <div class="bg-white rounded-2xl shadow border max-w-xs w-full p-5">
              <div class="text-center mb-4">
                <h4 class="font-bold text-gray-900">{lang === 'pt' ? 'Agende uma conversa' : lang === 'fr' ? 'Planifier un appel' : lang === 'en' ? 'Book a call' : 'Agende una conversación'}</h4>
                <p class="text-xs text-gray-400">{lang === 'pt' ? 'Preencha seus dados' : lang === 'fr' ? 'Remplissez vos données' : lang === 'en' ? 'Fill in your info' : 'Complete sus datos'}</p>
              </div>
              <div class="space-y-2 mb-4">
                <div class="bg-gray-50 rounded-lg px-3 py-2 border text-sm text-gray-700">Maria Santos</div>
                <div class="bg-gray-50 rounded-lg px-3 py-2 border text-sm text-gray-700">maria@email.com</div>
                <div class="bg-gray-50 rounded-lg px-3 py-2 border text-sm text-gray-400">(11) 99999-0000</div>
              </div>
              <div class="bg-blue-600 text-white text-center py-2 rounded-lg text-sm font-semibold">{lang === 'pt' ? 'Começar' : lang === 'fr' ? 'Commencer' : lang === 'en' ? 'Start' : 'Empezar'}</div>
            </div>
          </div>
          <div class="bg-white px-4 py-2 border-t text-center"><span class="text-xs text-gray-400 font-semibold">1️⃣ {lang === 'pt' ? 'Lead preenche nome, email e telefone' : lang === 'fr' ? 'Le lead remplit nom, email et téléphone' : lang === 'en' ? 'Lead fills name, email and phone' : 'El lead completa nombre, email y teléfono'}</span></div>
        </div>

        <!-- Step B: Question -->
        <div class="border-2 border-gray-200 rounded-2xl overflow-hidden shadow-lg">
          <div class="bg-gray-100 px-4 py-2 flex items-center gap-2 border-b">
            <div class="flex gap-1.5"><div class="w-3 h-3 rounded-full bg-red-400"></div><div class="w-3 h-3 rounded-full bg-yellow-400"></div><div class="w-3 h-3 rounded-full bg-green-400"></div></div>
            <div class="flex-1 text-center text-xs text-gray-400">{lang === 'pt' ? 'Pergunta 2 / 5' : lang === 'fr' ? 'Question 2 / 5' : lang === 'en' ? 'Question 2 / 5' : 'Pregunta 2 / 5'}</div>
          </div>
          <div class="bg-gradient-to-b from-gray-50 to-gray-100 p-6 flex justify-center">
            <div class="bg-white rounded-2xl shadow border max-w-xs w-full p-5">
              <div class="bg-gray-50 px-3 py-2 rounded-lg mb-4 flex items-center justify-between">
                <span class="text-xs text-gray-500">2/5</span>
                <div class="w-20 bg-gray-200 rounded-full h-1.5"><div class="bg-blue-600 h-1.5 rounded-full" style="width: 40%"></div></div>
              </div>
              <h4 class="font-bold text-gray-900 mb-4">{lang === 'pt' ? 'Qual a sua faixa salarial?' : lang === 'fr' ? 'Quelle est votre tranche salariale ?' : lang === 'en' ? 'What is your salary range?' : '¿Cuál es su rango salarial?'}</h4>
              <div class="grid grid-cols-2 gap-2">
                <div class="border-2 border-gray-200 rounded-xl px-3 py-3 text-center text-xs font-medium text-gray-600">R$ 3-5k</div>
                <div class="border-2 border-blue-500 bg-blue-50 rounded-xl px-3 py-3 text-center text-xs font-medium text-blue-700">R$ 5-10k</div>
                <div class="border-2 border-gray-200 rounded-xl px-3 py-3 text-center text-xs font-medium text-gray-600">R$ 10-20k</div>
                <div class="border-2 border-gray-200 rounded-xl px-3 py-3 text-center text-xs font-medium text-gray-600">R$ 20k+</div>
              </div>
            </div>
          </div>
          <div class="bg-white px-4 py-2 border-t text-center"><span class="text-xs text-gray-400 font-semibold">2️⃣ {lang === 'pt' ? 'Lead responde perguntas de qualificação' : lang === 'fr' ? 'Le lead répond aux questions de qualification' : lang === 'en' ? 'Lead answers qualifying questions' : 'El lead responde preguntas de calificación'}</span></div>
        </div>

        <!-- Step C: Calendar -->
        <div class="border-2 border-gray-200 rounded-2xl overflow-hidden shadow-lg">
          <div class="bg-gray-100 px-4 py-2 flex items-center gap-2 border-b">
            <div class="flex gap-1.5"><div class="w-3 h-3 rounded-full bg-red-400"></div><div class="w-3 h-3 rounded-full bg-yellow-400"></div><div class="w-3 h-3 rounded-full bg-green-400"></div></div>
            <div class="flex-1 text-center text-xs text-gray-400">{lang === 'pt' ? 'Escolha o dia' : lang === 'fr' ? 'Choisissez le jour' : lang === 'en' ? 'Pick a day' : 'Elija el día'}</div>
          </div>
          <div class="bg-gradient-to-b from-gray-50 to-gray-100 p-6 flex justify-center">
            <div class="bg-white rounded-2xl shadow border max-w-xs w-full p-4">
              <div class="flex items-center justify-between mb-3 px-1">
                <span class="text-xs text-gray-400">◀</span>
                <span class="text-sm font-bold text-gray-800">{lang === 'fr' ? 'Mars' : lang === 'en' ? 'March' : lang === 'es' ? 'Marzo' : 'Março'} 2026</span>
                <span class="text-xs text-gray-400">▶</span>
              </div>
              <div class="grid grid-cols-7 gap-1 text-center text-[10px] font-bold text-gray-400 mb-1">
                <span>D</span><span>S</span><span>T</span><span>Q</span><span>Q</span><span>S</span><span>S</span>
              </div>
              <div class="grid grid-cols-7 gap-1 text-center text-xs">
                {#each [0,0,0,0,0,0,1] as d}{#if d}<span class="py-1.5 text-gray-300">1</span>{:else}<span></span>{/if}{/each}
                {#each [2,3,4,5,6,7,8] as d}<span class="py-1.5 {d>=2 && d<=6 ? 'text-gray-800 font-medium' : 'text-gray-300'}">{d}</span>{/each}
                {#each [9,10,11,12,13,14,15] as d}<span class="py-1.5 {d>=9 && d<=13 ? 'text-gray-800 font-medium' : 'text-gray-300'}">{d}</span>{/each}
                {#each [16,17,18,19,20,21,22] as d}<span class="py-1.5 {d>=16 && d<=20 ? 'text-gray-800 font-medium' : 'text-gray-300'}">{d}</span>{/each}
                {#each [23,24,25,26,27,28,29] as d}<span class="py-1.5 {d === 25 ? 'bg-blue-600 text-white rounded-lg font-bold' : d>=23 && d<=27 ? 'text-gray-800 font-medium' : 'text-gray-300'}">{d}</span>{/each}
              </div>
            </div>
          </div>
          <div class="bg-white px-4 py-2 border-t text-center"><span class="text-xs text-gray-400 font-semibold">3️⃣ {lang === 'pt' ? 'Lead escolhe o dia no calendário' : lang === 'fr' ? 'Le lead choisit le jour sur le calendrier' : lang === 'en' ? 'Lead picks the day on the calendar' : 'El lead elige el día en el calendario'}</span></div>
        </div>

        <!-- Step D: Time -->
        <div class="border-2 border-gray-200 rounded-2xl overflow-hidden shadow-lg">
          <div class="bg-gray-100 px-4 py-2 flex items-center gap-2 border-b">
            <div class="flex gap-1.5"><div class="w-3 h-3 rounded-full bg-red-400"></div><div class="w-3 h-3 rounded-full bg-yellow-400"></div><div class="w-3 h-3 rounded-full bg-green-400"></div></div>
            <div class="flex-1 text-center text-xs text-gray-400">{lang === 'pt' ? 'Escolha o horário' : lang === 'fr' ? 'Choisissez l\'heure' : lang === 'en' ? 'Pick a time' : 'Elija el horario'}</div>
          </div>
          <div class="bg-gradient-to-b from-gray-50 to-gray-100 p-6 flex justify-center">
            <div class="bg-white rounded-2xl shadow border max-w-xs w-full p-5">
              <p class="text-[10px] font-bold text-gray-400 uppercase mb-2">{lang === 'pt' ? 'Manhã' : lang === 'fr' ? 'Matin' : lang === 'en' ? 'Morning' : 'Mañana'}</p>
              <div class="grid grid-cols-3 gap-2 mb-3">
                <div class="border-2 border-gray-200 rounded-xl py-2 text-center text-xs font-semibold text-gray-600">09:00</div>
                <div class="border-2 border-gray-200 rounded-xl py-2 text-center text-xs font-semibold text-gray-600">09:30</div>
                <div class="border-2 border-blue-500 bg-blue-50 rounded-xl py-2 text-center text-xs font-bold text-blue-700">10:00</div>
              </div>
              <p class="text-[10px] font-bold text-gray-400 uppercase mb-2">{lang === 'pt' ? 'Tarde' : lang === 'fr' ? 'Après-midi' : lang === 'en' ? 'Afternoon' : 'Tarde'}</p>
              <div class="grid grid-cols-3 gap-2">
                <div class="border-2 border-gray-200 rounded-xl py-2 text-center text-xs font-semibold text-gray-600">14:00</div>
                <div class="border-2 border-gray-200 rounded-xl py-2 text-center text-xs font-semibold text-gray-600">15:00</div>
                <div class="border-2 border-gray-200 rounded-xl py-2 text-center text-xs font-semibold text-gray-600">16:00</div>
              </div>
              <div class="bg-blue-600 text-white text-center py-2 rounded-lg text-sm font-semibold mt-4">{lang === 'pt' ? 'Continuar' : lang === 'fr' ? 'Continuer' : lang === 'en' ? 'Continue' : 'Continuar'}</div>
            </div>
          </div>
          <div class="bg-white px-4 py-2 border-t text-center"><span class="text-xs text-gray-400 font-semibold">4️⃣ {lang === 'pt' ? 'Lead escolhe o horário disponível' : lang === 'fr' ? 'Le lead choisit l\'heure disponible' : lang === 'en' ? 'Lead picks available time' : 'El lead elige el horario disponible'}</span></div>
        </div>

        <!-- Step E: Confirmed -->
        <div class="border-2 border-green-300 rounded-2xl overflow-hidden shadow-lg">
          <div class="bg-green-50 p-8 text-center">
            <div class="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
              <svg class="w-8 h-8 text-green-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <h4 class="text-lg font-bold text-gray-900">{lang === 'pt' ? 'Agendamento Confirmado!' : lang === 'fr' ? 'Rendez-vous Confirmé !' : lang === 'en' ? 'Booking Confirmed!' : '¡Agendamiento Confirmado!'}</h4>
            <p class="text-sm text-gray-500 mt-1">{lang === 'pt' ? '25 de março, 10:00' : lang === 'fr' ? '25 mars, 10h00' : lang === 'en' ? 'March 25, 10:00 AM' : '25 de marzo, 10:00'}</p>
            <div class="mt-3 inline-flex items-center gap-1.5 bg-white border border-green-200 rounded-lg px-3 py-1.5 text-xs text-green-700">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" /></svg>
              Google Calendar
            </div>
          </div>
          <div class="bg-white px-4 py-2 border-t text-center"><span class="text-xs text-gray-400 font-semibold">5️⃣ {lang === 'pt' ? 'Pronto! Evento criado no Google Calendar' : lang === 'fr' ? 'C\'est fait ! Événement créé dans Google Calendar' : lang === 'en' ? 'Done! Event created in Google Calendar' : '¡Listo! Evento creado en Google Calendar'}</span></div>
        </div>
      </div>
    </section>

    <!-- PASSO A PASSO -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-green-600 uppercase tracking-widest mb-2">03</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-8">{_('guideTitle')}</h3>
      {#each [
        { n: 1, tk: 'step1t', dk: 'step1d' },
        { n: 2, tk: 'step2t', dk: 'step2d' },
        { n: 3, tk: 'step3t', dk: 'step3d' },
        { n: 4, tk: 'step4t', dk: 'step4d' }
      ] as step}
        <div class="mb-8 flex gap-4">
          <div class="w-9 h-9 rounded-full bg-green-600 text-white flex items-center justify-center text-sm font-black flex-shrink-0">{step.n}</div>
          <div>
            <h4 class="text-lg font-bold text-gray-900 mb-1">{_(step.tk)}</h4>
            <p class="text-gray-600 leading-relaxed">{_(step.dk)}</p>
          </div>
        </div>
      {/each}

      <!-- Mockup: end node config -->
      <div class="ml-13 bg-white border-2 border-purple-200 rounded-2xl p-5 shadow-md mt-2">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-2.5 h-2.5 rounded-full bg-purple-500"></div>
          <span class="text-xs font-bold text-gray-700 uppercase">{lang === 'pt' ? 'Nó Final' : lang === 'fr' ? 'Nœud Final' : lang === 'en' ? 'End Node' : 'Nodo Final'}</span>
        </div>
        <div class="mb-2">
          <span class="text-[10px] text-gray-500 uppercase font-semibold">{lang === 'pt' ? 'Tipo de finalização' : lang === 'fr' ? 'Type de finalisation' : lang === 'en' ? 'End type' : 'Tipo de finalización'}</span>
        </div>
        <div class="border-2 border-green-400 bg-green-50 rounded-lg px-3 py-2.5 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25" /></svg>
          <span class="text-sm font-semibold text-green-800">{lang === 'pt' ? 'Agendamento (Calendário)' : lang === 'fr' ? 'Rendez-vous (Calendrier)' : lang === 'en' ? 'Scheduling (Calendar)' : 'Agendamiento (Calendario)'}</span>
          <span class="ml-auto text-green-600">✓</span>
        </div>
        <p class="text-[10px] text-gray-400 mt-2">{lang === 'pt' ? '↑ Essa opção ativa o calendário para o lead' : lang === 'fr' ? '↑ Cette option active le calendrier pour le lead' : lang === 'en' ? '↑ This option activates the calendar for the lead' : '↑ Esta opción activa el calendario para el lead'}</p>
      </div>
    </section>

    <!-- DASHBOARD -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-green-600 uppercase tracking-widest mb-2">04</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-4">{_('dashTitle')}</h3>
      <p class="text-gray-600 mb-6">{_('dashP')}</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-green-50 rounded-2xl p-5 border border-green-200">
          <span class="text-lg mb-2 block">📋</span>
          <p class="text-sm font-semibold text-gray-800">{_('dashTab1')}</p>
        </div>
        <div class="bg-blue-50 rounded-2xl p-5 border border-blue-200">
          <span class="text-lg mb-2 block">📅</span>
          <p class="text-sm font-semibold text-gray-800">{_('dashTab2')}</p>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="mb-16">
      <h2 class="text-sm font-bold text-green-600 uppercase tracking-widest mb-2">05</h2>
      <h3 class="text-2xl font-bold text-gray-900 mb-6">{_('faqTitle')}</h3>
      <div class="space-y-2">
        {#each [
          { q: 'faq1q', a: 'faq1a' },
          { q: 'faq2q', a: 'faq2a' },
          { q: 'faq3q', a: 'faq3a' }
        ] as faq, idx}
          <button onclick={() => toggleFaq(idx)} class="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-xl px-5 py-4 transition-colors cursor-pointer">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-gray-800">{_(faq.q)}</span>
              <svg class="w-5 h-5 text-gray-400 transition-transform {expandedFaq === idx ? 'rotate-180' : ''}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" /></svg>
            </div>
            {#if expandedFaq === idx}
              <p class="text-sm text-gray-600 mt-3 leading-relaxed">{_(faq.a)}</p>
            {/if}
          </button>
        {/each}
      </div>
    </section>

    <!-- CTA -->
    <div class="text-center pb-16">
      <button
        onclick={() => goto('/admin/scheduling')}
        class="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-10 py-4 rounded-2xl text-lg font-bold hover:shadow-xl cursor-pointer transition-all shadow-lg active:scale-95"
      >
        {_('cta')} →
      </button>
    </div>
  </main>
</div>
