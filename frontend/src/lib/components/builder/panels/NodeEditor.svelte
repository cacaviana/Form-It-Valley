<script lang="ts">
  import type { Node } from '@xyflow/svelte';
  import type { FlowNodeData, QuestionType, FlowOption } from '$lib/dto/flows/types';

  let { node, onUpdate, onDelete, onClose, catalogItems = [] } = $props<{
    node: Node;
    onUpdate: (data: Partial<FlowNodeData>) => void;
    onDelete: () => void;
    onClose: () => void;
    catalogItems?: string[]; // Nomes dos produtos do CSV carregado
  }>();

  let data = $derived(node.data as FlowNodeData);

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
    { value: 'quote', label: 'Générer devis (IA)' },
    { value: 'specialist', label: 'Contact spécialiste' },
    { value: 'thank_you', label: 'Remerciement' },
    { value: 'scheduling', label: 'Rendez-vous (Calendrier)' }
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
        <label class="label">Type de finalisation</label>
        <select
          value={data.endType || 'quote'}
          onchange={(e) => onUpdate({ endType: (e.target as HTMLSelectElement).value as 'quote' | 'specialist' | 'thank_you' | 'scheduling' })}
          class="input"
        >
          {#each endTypes as et}
            <option value={et.value}>{et.label}</option>
          {/each}
        </select>
      </div>

      {#if data.endType === 'quote'}
        <!-- Tabela de preços -->
        <div>
          <div class="flex items-center gap-1.5 mb-1">
            <svg class="w-3.5 h-3.5 text-green-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <label class="label !mb-0">Tableau de prix</label>
          </div>
          <textarea
            value={data.businessContext || ''}
            oninput={(e) => onUpdate({ businessContext: (e.target as HTMLTextAreaElement).value })}
            class="input h-36 resize-y font-mono text-xs"
            placeholder={"Ex:\nBorne 32A Level 2: $699\nInstallation murale: $250\nCâblage (25-50 pieds): +$150\nUpgrade panneau 100A→200A: $1,800"}
          ></textarea>
          <p class="text-xs text-gray-400 mt-1">Listez tous les produits et prix. L'IA utilise ce tableau pour calculer le devis.</p>
        </div>

        <!-- Regras de negócio -->
        <div>
          <div class="flex items-center gap-1.5 mb-1">
            <svg class="w-3.5 h-3.5 text-amber-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            <label class="label !mb-0">Règles d'affaires</label>
          </div>
          <textarea
            value={data.aiInstruction || ''}
            oninput={(e) => onUpdate({ aiInstruction: (e.target as HTMLTextAreaElement).value })}
            class="input h-28 resize-y text-xs"
            placeholder={"Ex:\n- Si panneau 100A et pas d'espaces libres → inclure upgrade 100A→200A ($1,800)\n- Borne Level 2 → appliquer subvention Roulez Vert (-$600)\n- Câblage: ajouter 15 pieds à la distance indiquée\n- Toujours inclure TPS (5%) et TVQ (9.975%)"}
          ></textarea>
          <p class="text-xs text-gray-400 mt-1">Indiquez quand appliquer chaque prix. Plus c'est clair, meilleur sera le devis.</p>
        </div>

        <!-- Aviso IA -->
        <div class="bg-amber-50 border border-amber-200 rounded-lg p-3">
          <div class="flex gap-2">
            <svg class="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
            </svg>
            <div>
              <p class="text-xs font-semibold text-amber-800">Règles claires = devis précis</p>
              <p class="text-xs text-amber-700 mt-1">Sans règles, l'IA peut oublier des articles ou se tromper dans les calculs. Décrivez les conditions de chaque prix.</p>
              <p class="text-xs text-amber-600 mt-1.5 italic">Même ainsi, les IAs peuvent se tromper. Vérifiez toujours le devis avant de l'envoyer au client.</p>
            </div>
          </div>
        </div>
      {/if}

      {#if data.endType === 'specialist'}
        <div>
          <label class="label">Message au client</label>
          <textarea
            value={data.message || ''}
            oninput={(e) => onUpdate({ message: (e.target as HTMLTextAreaElement).value })}
            class="input h-20 resize-y"
            placeholder="Ex : Un spécialiste vous contactera sous 24h..."
          ></textarea>
        </div>
      {/if}

      {#if data.endType === 'scheduling'}
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div class="flex gap-2">
            <svg class="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
            </svg>
            <div>
              <p class="text-xs font-semibold text-blue-800">Mode Rendez-vous</p>
              <p class="text-xs text-blue-700 mt-1">Le client choisit date et heure sur le calendrier. Le rendez-vous est créé dans Google Calendar et envoyé via webhook (WhatsApp).</p>
            </div>
          </div>
        </div>
        <div>
          <label class="label">Message de confirmation</label>
          <textarea
            value={data.message || ''}
            oninput={(e) => onUpdate({ message: (e.target as HTMLTextAreaElement).value })}
            class="input h-20 resize-y"
            placeholder="Ex : Choisissez le meilleur jour et heure pour notre conversation..."
          ></textarea>
        </div>
      {/if}
    {/if}

    <!-- ==================== START ==================== -->
    {#if node.type === 'start'}
      <div class="bg-green-50 rounded-lg p-3 text-sm text-green-700">
        Point d'entrée du flux. Collecte automatiquement : nom, email, téléphone et adresse du client.
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
