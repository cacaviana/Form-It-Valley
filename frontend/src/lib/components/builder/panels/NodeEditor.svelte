<script lang="ts">
  import type { Node } from '@xyflow/svelte';
  import type { FlowNodeData, QuestionType, FlowOption } from '$lib/dto/flows/types';
  import { authFetch } from '$lib/utils/auth-fetch';

  let { node, onUpdate, onDelete, onClose, catalogItems = [], acListId = '', acListName = '', onAcChange = (_id: string, _name: string) => {}, themeColor = 'violet', onThemeChange = (_color: string) => {} } = $props<{
    node: Node;
    onUpdate: (data: Partial<FlowNodeData>) => void;
    onDelete: () => void;
    onClose: () => void;
    catalogItems?: string[];
    acListId?: string;
    acListName?: string;
    onAcChange?: (listId: string, listName: string) => void;
    themeColor?: string;
    onThemeChange?: (color: string) => void;
  }>();

  const themeColors = [
    { id: 'violet', label: 'Roxo', color: '#7C3AED', light: '#EDE9FE' },
    { id: 'blue', label: 'Azul', color: '#2563EB', light: '#DBEAFE' },
    { id: 'emerald', label: 'Verde', color: '#059669', light: '#D1FAE5' },
    { id: 'rose', label: 'Rosa', color: '#E11D48', light: '#FFE4E6' },
    { id: 'orange', label: 'Laranja', color: '#EA580C', light: '#FFEDD5' },
    { id: 'cyan', label: 'Ciano', color: '#0891B2', light: '#CFFAFE' },
    { id: 'amber', label: 'Dourado', color: '#D97706', light: '#FEF3C7' },
    { id: 'slate', label: 'Escuro', color: '#334155', light: '#F1F5F9' },
  ];

  let data = $derived(node.data as FlowNodeData);

  // WhatsApp templates
  let waTemplates = $state<{ name: string; body: string; variableCount: number; category: string }[]>([]);
  let loadingTemplates = $state(false);
  let selectedTemplate = $derived(waTemplates.find(t => t.name === data.whatsappTemplate));

  // Preview resolvido do WhatsApp
  function getResolvedPreview(): string {
    if (!selectedTemplate) return '';
    const examples: Record<string, string> = {
      nome: 'Joao Silva', data: 'segunda-feira, 7 de abril de 2026',
      horario: '14:30', link: 'https://calendar.google.com/...',
      email: 'joao@email.com', telefone: '(27) 99513-0691'
    };
    const vars = data.whatsappVariables || [];
    return selectedTemplate.body.replace(/\{\{(\d+)\}\}/g, (_: string, num: string) => {
      const idx = parseInt(num) - 1;
      const varValue = vars[idx] || '{{' + num + '}}';
      return varValue.replace(/\{\{(\w+)\}\}/g, (_m: string, key: string) => examples[key] || '{{' + key + '}}');
    });
  }

  // ActiveCampaign lists — salva no nivel do Flow
  let acLists = $state<{ id: string; name: string; subscriber_count: number }[]>([]);
  let loadingAcLists = $state(false);

  async function loadAcLists() {
    if (acLists.length > 0) return;
    loadingAcLists = true;
    try {
      const res = await authFetch('/api/activecampaign/lists');
      if (res.ok) acLists = await res.json();
    } catch (e) { /* silent */ }
    loadingAcLists = false;
  }

  async function loadTemplates() {
    if (waTemplates.length > 0) return;
    loadingTemplates = true;
    try {
      const res = await authFetch('/api/whatsapp-templates');
      if (res.ok) {
        waTemplates = await res.json();
        // Auto-seleciona "agendamentos" como default se nenhum template estiver escolhido
        if (!data.whatsappTemplate && waTemplates.some(t => t.name === 'agendamentos')) {
          onTemplateChange('agendamentos');
        }
      }
    } catch (e) { /* silent */ }
    loadingTemplates = false;
  }


  // Carrega templates quando end type for scheduling
  $effect(() => {
    if (node.type === 'end' && data.endType === 'scheduling') {
      loadTemplates();
    }
  });

  // Carrega listas AC quando for end node
  $effect(() => {
    if (node.type === 'end') {
      loadAcLists();
    }
  });


  const placeholderOptions = [
    { value: '{{nome}}', label: 'Nome do lead' },
    { value: '{{data}}', label: 'Data do agendamento' },
    { value: '{{horario}}', label: 'Horário do agendamento' },
    { value: '{{link}}', label: 'Link do Google Calendar' },
    { value: '{{email}}', label: 'E-mail do lead' },
    { value: '{{telefone}}', label: 'Telefone do lead' }
  ];

  function updateVariable(index: number, value: string) {
    const vars = [...(data.whatsappVariables || [])];
    vars[index] = value;
    onUpdate({ whatsappVariables: vars });
  }

  function onTemplateChange(templateName: string) {
    const tpl = waTemplates.find(t => t.name === templateName);
    // Inicializa variaveis com placeholders padrao
    const vars: string[] = [];
    if (tpl) {
      for (let i = 0; i < tpl.variableCount; i++) {
        if (i === 0) vars.push('{{nome}}');
        else if (i === 1) vars.push('Seu atendimento na IT Valley foi confirmado! Data: {{data}} - Horário: {{horario}}');
        else if (i === 2) vars.push('Link da reunião: {{link}}');
        else vars.push('');
      }
    }
    onUpdate({ whatsappTemplate: templateName, whatsappVariables: vars });
  }

  const questionTypes: { value: QuestionType; label: string; hint: string }[] = [
    { value: 'single_choice', label: 'Choix unique', hint: 'Le client choisit 1 option (chaque option devient une sortie du flux)' },
    { value: 'yes_no', label: 'Oui / Non', hint: '2 sorties : Oui ou Non — idéal pour les bifurcations' },
    { value: 'number', label: 'Quantité', hint: 'Champ numérique — liez à un produit du CSV pour calculer quantité x prix' },
    { value: 'text', label: 'Texte libre', hint: 'Champ ouvert pour observations (ne devient jamais un article du devis)' },
    { value: 'multiple_choice', label: 'Choix multiple', hint: 'Le client peut sélectionner plusieurs options' },
    { value: 'date', label: 'Date', hint: 'Sélecteur de date — ne devient jamais un article du devis' },
    { value: 'dropdown', label: 'Liste déroulante', hint: 'Sélecteur dropdown pour les longues listes' },
    { value: 'photo', label: 'Envoi de photo', hint: 'Le client envoie une photo — ne devient jamais un article du devis' }
  ];

  const endTypes = [
    { value: 'scheduling', label: 'Agendar Atendimento' },
    { value: 'finish', label: 'Finalizar' }
  ];

  // Which question types have individual option handles (branching)
  const branchingTypes: QuestionType[] = ['single_choice', 'yes_no', 'multiple_choice', 'dropdown'];
  let hasBranching = $derived(branchingTypes.includes(data.questionType || 'text'));

  function addOption() {
    const options = [...(data.options || [])];
    const idx = options.length + 1;
    options.push({
      id: 'opt_' + crypto.randomUUID().slice(0, 6),
      label: `Opção ${idx}`,
      value: `opcao_${idx}`
    });
    onUpdate({ options });
  }

  function removeOption(optId: string) {
    onUpdate({ options: (data.options || []).filter(o => o.id !== optId) });
  }

  function updateOption(optId: string, field: keyof FlowOption, value: string) {
    onUpdate({
      options: (data.options || []).map(o =>
        o.id === optId ? { ...o, [field]: value } : o
      )
    });
  }

  const typeColors: Record<string, string> = {
    start: 'bg-green-500',
    question: 'bg-blue-500',
    message: 'bg-gray-500',
    end: 'bg-purple-500'
  };

  const typeLabels: Record<string, string> = {
    start: 'Début',
    question: 'Question',
    message: 'Message',
    end: 'Fin'
  };
</script>

<div class="w-80 bg-white border-l border-gray-200 h-full overflow-y-auto">
  <!-- Header -->
  <div class="sticky top-0 bg-white border-b border-gray-100 px-4 py-3 flex justify-between items-center z-10">
    <div class="flex items-center gap-2">
      <div class="w-2.5 h-2.5 rounded-full {typeColors[node.type || 'question']}"></div>
      <span class="font-semibold text-sm text-gray-900">{typeLabels[node.type || 'question']}</span>
    </div>
    <button onclick={onClose} class="w-7 h-7 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-400 hover:text-gray-600 cursor-pointer transition-colors">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  <div class="p-4 space-y-4">
    <!-- Título — all types -->
    <div>
      <label class="label">Titre</label>
      <input
        type="text"
        value={data.title}
        oninput={(e) => onUpdate({ title: (e.target as HTMLInputElement).value })}
        class="input"
      />
    </div>

    <!-- ==================== QUESTION ==================== -->
    {#if node.type === 'question'}
      <div>
        <label class="label">Type de question</label>
        <select
          value={data.questionType}
          onchange={(e) => onUpdate({ questionType: (e.target as HTMLSelectElement).value as QuestionType })}
          class="input"
        >
          {#each questionTypes as qt}
            <option value={qt.value}>{qt.label}</option>
          {/each}
        </select>
        <p class="text-xs text-gray-400 mt-1">{questionTypes.find(q => q.value === data.questionType)?.hint || ''}</p>
      </div>

      <div>
        <label class="label">Astuce (tooltip)</label>
        <input
          type="text"
          value={data.tooltip || ''}
          oninput={(e) => onUpdate({ tooltip: (e.target as HTMLInputElement).value })}
          class="input"
          placeholder="Texte d'aide pour le client"
        />
      </div>

      <div class="flex items-center gap-2">
        <input
          type="checkbox"
          id="required"
          checked={data.required !== false}
          onchange={(e) => onUpdate({ required: (e.target as HTMLInputElement).checked })}
          class="rounded border-gray-300"
        />
        <label for="required" class="text-sm text-gray-700">Obligatoire</label>
      </div>

      <!-- Options for choice-based types -->
      {#if data.questionType === 'single_choice' || data.questionType === 'multiple_choice' || data.questionType === 'dropdown'}
        <div>
          <div class="flex justify-between items-center mb-2">
            <label class="label !mb-0">Options</label>
            <button onclick={addOption} class="text-xs text-blue-600 hover:text-blue-800 cursor-pointer font-medium">+ Ajouter</button>
          </div>
          {#if hasBranching}
            <p class="text-xs text-blue-500 mb-2">Chaque option crée une sortie — connectez au nœud suivant</p>
          {/if}

          <!-- Aviso se CSV carregado mas alguma opção sem produto vinculado -->
          {#if catalogItems.length > 0}
            {@const semProduto = (data.options || []).filter(o => !o.catalogProduct)}
            {#if semProduto.length > 0}
              <div class="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mb-2 flex gap-2 items-start">
                <svg class="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                </svg>
                <p class="text-xs text-amber-700">
                  {semProduto.length === 1 ? '1 option sans' : `${semProduto.length} option(s) sans`} produit lié au CSV.
                  L'IA peut halluciner.
                </p>
              </div>
            {/if}
          {/if}

          <div class="space-y-2">
            {#each data.options || [] as opt}
              <div class="border border-gray-100 rounded-lg p-2 space-y-1.5 bg-gray-50/50">
                <!-- Label da opção -->
                <div class="flex gap-1.5 items-center">
                  <input
                    type="text"
                    value={opt.label}
                    oninput={(e) => updateOption(opt.id, 'label', (e.target as HTMLInputElement).value)}
                    class="input !py-1.5 flex-1 bg-white"
                    placeholder="Texte de l'option"
                  />
                  <button onclick={() => removeOption(opt.id)} class="w-7 h-7 flex-shrink-0 rounded hover:bg-red-50 flex items-center justify-center text-gray-400 hover:text-red-500 cursor-pointer">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <!-- Produto no catálogo (só aparece se CSV foi carregado) -->
                {#if catalogItems.length > 0}
                  <div class="flex items-center gap-1.5">
                    {#if opt.catalogProduct}
                      <svg class="w-3 h-3 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
                      </svg>
                    {:else}
                      <svg class="w-3 h-3 text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                      </svg>
                    {/if}
                    <input
                      list="catalog-{opt.id}"
                      type="text"
                      value={opt.catalogProduct || ''}
                      oninput={(e) => updateOption(opt.id, 'catalogProduct', (e.target as HTMLInputElement).value)}
                      onchange={(e) => updateOption(opt.id, 'catalogProduct', (e.target as HTMLInputElement).value)}
                      class="input !py-1 text-xs flex-1 bg-white {opt.catalogProduct ? 'border-green-300 text-green-800' : 'border-amber-200 text-gray-500'}"
                      placeholder="Lier au produit du CSV..."
                    />
                    <datalist id="catalog-{opt.id}">
                      {#each catalogItems as item}
                        <option value={item} />
                      {/each}
                    </datalist>
                    {#if opt.catalogProduct}
                      <button
                        onclick={() => updateOption(opt.id, 'catalogProduct', '')}
                        class="text-gray-300 hover:text-red-400 cursor-pointer flex-shrink-0"
                        title="Retirer le lien"
                      >
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    {/if}
                  </div>
                {/if}
              </div>
            {/each}
          </div>

          {#if catalogItems.length === 0}
            <p class="text-xs text-gray-400 mt-1.5">Chargez un CSV de prix pour lier chaque option à un produit du catalogue.</p>
          {/if}
        </div>
      {/if}

      <!-- Rating max -->
      {#if data.questionType === 'rating'}
        <div>
          <label class="label">Échelle maximale</label>
          <input
            type="number"
            value={data.ratingMax || 5}
            min="3"
            max="10"
            oninput={(e) => onUpdate({ ratingMax: parseInt((e.target as HTMLInputElement).value) || 5 })}
            class="input"
          />
        </div>
      {/if}

      <!-- Quantity product association (number) -->
      {#if data.questionType === 'number' && catalogItems.length > 0}
        <div>
          <label class="label">Quantité de quel produit ?</label>
          <p class="text-xs text-gray-400 mb-1.5">La réponse numérique sera utilisée comme quantité de ce produit dans le devis.</p>
          <div class="flex items-center gap-1.5">
            {#if data.quantityProduct}
              <svg class="w-3 h-3 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
              </svg>
            {:else}
              <svg class="w-3 h-3 text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
            {/if}
            <input
              list="catalog-qty-{node.id}"
              type="text"
              value={data.quantityProduct || ''}
              oninput={(e) => onUpdate({ quantityProduct: (e.target as HTMLInputElement).value })}
              class="input !py-1 text-xs flex-1 bg-white {data.quantityProduct ? 'border-green-300 text-green-800' : 'border-amber-200 text-gray-500'}"
              placeholder="Vincular a produto do CSV..."
            />
            <datalist id="catalog-qty-{node.id}">
              {#each catalogItems as item}
                <option value={item} />
              {/each}
            </datalist>
            {#if data.quantityProduct}
              <button
                onclick={() => onUpdate({ quantityProduct: '' })}
                class="text-gray-300 hover:text-red-400 cursor-pointer flex-shrink-0"
                title="Remover vínculo"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            {/if}
          </div>
        </div>
      {/if}

      <!-- Photo hint -->
      {#if data.questionType === 'photo'}
        <div class="bg-blue-50 rounded-lg p-3 text-xs text-blue-700">
          Le client pourra envoyer une photo du lieu/équipement. L'image sera sauvegardée avec les réponses.
        </div>
      {/if}

      <!-- Date hint -->
      {#if data.questionType === 'date'}
        <div class="bg-blue-50 rounded-lg p-3 text-xs text-blue-700">
          Le client verra un sélecteur de date. Utile pour planifier des visites ou dates préférentielles.
        </div>
      {/if}
    {/if}

    <!-- ==================== MESSAGE ==================== -->
    {#if node.type === 'message'}
      <div class="flex items-center gap-2">
        <input
          type="checkbox"
          id="isSpecialist"
          checked={data.isSpecialist === true}
          onchange={(e) => onUpdate({ isSpecialist: (e.target as HTMLInputElement).checked })}
          class="rounded border-gray-300"
        />
        <label for="isSpecialist" class="text-sm text-gray-700">Rediriger vers un spécialiste</label>
      </div>
      {#if data.isSpecialist}
        <div class="bg-red-50 rounded-lg p-3 text-xs text-red-600">
          Le client sera informé qu'un spécialiste le contactera. Les données seront enregistrées comme lead.
        </div>
      {/if}
      <div>
        <label class="label">Texte du message</label>
        <textarea
          value={data.message || ''}
          oninput={(e) => onUpdate({ message: (e.target as HTMLTextAreaElement).value })}
          class="input h-24 resize-y"
          placeholder="Texte que le client verra..."
        ></textarea>
      </div>
    {/if}

    <!-- ==================== END ==================== -->
    {#if node.type === 'end'}
      <div>
        <label class="label">Tipo de finalizacao</label>
        <select
          value={data.endType || 'finish'}
          onchange={(e) => onUpdate({ endType: (e.target as HTMLSelectElement).value as 'scheduling' | 'finish' })}
          class="input"
        >
          {#each endTypes as et}
            <option value={et.value}>{et.label}</option>
          {/each}
        </select>
      </div>

      {#if data.endType === 'scheduling'}
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div class="flex gap-2">
            <svg class="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
            </svg>
            <div>
              <p class="text-xs font-semibold text-blue-800">Agendar Atendimento</p>
              <p class="text-xs text-blue-700 mt-1">O lead escolhe data e horário no calendário. O agendamento é criado no Google Calendar, e o lead recebe um e-mail com o link da call e uma mensagem no WhatsApp.</p>
            </div>
          </div>
        </div>
        <div>
          <label class="label">Mensagem de confirmação</label>
          <textarea
            value={data.message || ''}
            oninput={(e) => onUpdate({ message: (e.target as HTMLTextAreaElement).value })}
            class="input h-20 resize-y"
            placeholder="Ex: Escolha o melhor dia e horário para nossa conversa..."
          ></textarea>
        </div>

        <!-- WhatsApp Template Config -->
        <div class="border-t border-gray-200 pt-4 mt-2">
          <div class="flex items-center gap-1.5 mb-3">
            <svg class="w-4 h-4 text-green-600" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
              <path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.75.75 0 00.917.918l4.462-1.494A11.943 11.943 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-2.337 0-4.542-.664-6.407-1.813l-.456-.276-2.653.888.889-2.651-.277-.458A9.953 9.953 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/>
            </svg>
            <label class="label !mb-0">Template WhatsApp</label>
          </div>

          {#if loadingTemplates}
            <div class="text-xs text-gray-400 py-2">Carregando templates...</div>
          {:else if waTemplates.length === 0}
            <div class="text-xs text-gray-400 py-2">Nenhum template disponível</div>
          {:else}
            <select
              value={data.whatsappTemplate || ''}
              onchange={(e) => onTemplateChange((e.target as HTMLSelectElement).value)}
              class="input mb-2"
            >
              <option value="">Selecione um template</option>
              {#each waTemplates as tpl}
                <option value={tpl.name}>{tpl.name} ({tpl.variableCount} vars)</option>
              {/each}
            </select>

            {#if selectedTemplate}
              <!-- Variaveis -->
              {#if selectedTemplate.variableCount > 0}
                <div class="space-y-2 mb-3">
                  <p class="text-xs font-semibold text-gray-500 uppercase">Variaveis do template</p>
                  <div class="bg-blue-50 border border-blue-100 rounded-lg px-3 py-2 mb-1">
                    <p class="text-xs text-blue-700">Placeholders disponiveis:</p>
                    <div class="flex flex-wrap gap-1 mt-1">
                      {#each placeholderOptions as ph}
                        <button
                          type="button"
                          class="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-mono hover:bg-blue-200 cursor-pointer"
                          title="Clique para copiar: {ph.value} — {ph.label}"
                          onclick={() => navigator.clipboard.writeText(ph.value)}
                        >{ph.value}</button>
                      {/each}
                    </div>
                  </div>
                  {#each Array(selectedTemplate.variableCount) as _, i}
                    <div>
                      <label class="text-xs text-gray-500 mb-0.5 block">
                        Variavel {`{{${i + 1}}}`}
                      </label>
                      <input
                        type="text"
                        value={(data.whatsappVariables || [])[i] || ''}
                        oninput={(e) => updateVariable(i, (e.target as HTMLInputElement).value)}
                        class="input !py-1.5 text-xs font-mono"
                        placeholder={'Ex: {{nome}}'}
                      />
                    </div>
                  {/each}
                </div>
              {/if}

              <!-- Preview da mensagem -->
              <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                <div class="flex items-center gap-1.5 mb-2">
                  <svg class="w-3.5 h-3.5 text-green-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
                  </svg>
                  <p class="text-xs font-semibold text-green-800">Preview da mensagem</p>
                </div>
                <p class="text-xs text-green-900 whitespace-pre-wrap leading-relaxed">{getResolvedPreview()}</p>
              </div>
            {/if}
          {/if}
        </div>
      {/if}

      {#if data.endType === 'finish'}
        <div class="bg-green-50 border border-green-200 rounded-lg p-3">
          <div class="flex gap-2">
            <svg class="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
            </svg>
            <div>
              <p class="text-xs font-semibold text-green-800">Finalizar</p>
              <p class="text-xs text-green-700 mt-1">O lead verá uma mensagem de agradecimento ao final do formulário.</p>
            </div>
          </div>
        </div>
        <div>
          <label class="label">Mensagem final</label>
          <textarea
            value={data.message || ''}
            oninput={(e) => onUpdate({ message: (e.target as HTMLTextAreaElement).value })}
            class="input h-20 resize-y"
            placeholder="Ex: Obrigado pelas suas respostas! Entraremos em contato em breve."
          ></textarea>
        </div>
      {/if}

      <!-- ActiveCampaign — salva no nivel do Flow -->
      <div class="border-t border-gray-200 pt-4 mt-2">
        <div class="flex items-center gap-1.5 mb-3">
          <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <label class="label !mb-0">ActiveCampaign</label>
        </div>

        {#if loadingAcLists}
          <div class="text-xs text-gray-400 py-2">Carregando listas...</div>
        {:else if acLists.length === 0}
          <div class="text-xs text-gray-400 py-2">Nenhuma lista disponível. Verifique as credenciais do ActiveCampaign.</div>
        {:else}
          <label class="text-xs text-gray-500 mb-1 block">Salvar lead na lista:</label>
          <select
            value={acListId || ''}
            onchange={(e) => {
              const listId = (e.target as HTMLSelectElement).value;
              const list = acLists.find(l => l.id === listId);
              onAcChange(listId || '', list?.name || '');
            }}
            class="input"
          >
            <option value="">Não salvar no ActiveCampaign</option>
            {#each acLists as list}
              <option value={list.id}>{list.name} ({list.subscriber_count} contatos)</option>
            {/each}
          </select>

          {#if acListId}
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-2 mt-2">
              <p class="text-xs text-blue-700">
                O lead sera automaticamente cadastrado na lista
                <strong>{acListName || acListId}</strong>
                ao clicar em "Começar" no formulário.
              </p>
            </div>
          {/if}
        {/if}
      </div>
    {/if}

    <!-- ==================== START ==================== -->
    {#if node.type === 'start'}
      <div class="bg-green-50 rounded-lg p-3 text-sm text-green-700 mb-4">
        Ponto de entrada do fluxo. Coleta automaticamente: nome, e-mail, telefone e endereço do lead.
      </div>

      <!-- Cor do formulário -->
      <div>
        <label class="label">Cor do formulário</label>
        <p class="text-xs text-gray-400 mb-3">Escolha a cor principal do formulário público</p>
        <div class="grid grid-cols-4 gap-2">
          {#each themeColors as tc}
            <button
              type="button"
              onclick={() => onThemeChange(tc.id)}
              class="flex flex-col items-center gap-1.5 p-2.5 rounded-xl border-2 transition-all cursor-pointer {themeColor === tc.id ? 'border-gray-900 shadow-sm' : 'border-transparent hover:bg-gray-50'}"
            >
              <div class="w-8 h-8 rounded-full shadow-sm" style="background: {tc.color};"></div>
              <span class="text-[10px] font-medium text-gray-600">{tc.label}</span>
            </button>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Delete button -->
    {#if node.type !== 'start'}
      <div class="pt-3 border-t border-gray-100">
        <button
          onclick={onDelete}
          class="w-full bg-red-50 text-red-600 border border-red-200 rounded-lg py-2 text-sm font-medium hover:bg-red-100 cursor-pointer transition-colors"
        >
          Supprimer le nœud
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.025em;
  }
  .input {
    width: 100%;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    transition: border-color 0.15s, box-shadow 0.15s;
    outline: none;
    background: white;
  }
  .input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
</style>
