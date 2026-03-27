<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { authFetch } from '$lib/utils/auth-fetch';
  import { onMount } from 'svelte';
  import {
    SvelteFlow,
    Controls,
    MiniMap,
    Background,
    BackgroundVariant,
    type NodeTypes
  } from '@xyflow/svelte';
  import type { Node, Edge, Connection } from '@xyflow/svelte';

  import StartNode from '$lib/components/builder/nodes/StartNode.svelte';
  import QuestionNode from '$lib/components/builder/nodes/QuestionNode.svelte';
  import MessageNode from '$lib/components/builder/nodes/MessageNode.svelte';
  import EndNode from '$lib/components/builder/nodes/EndNode.svelte';
  import NodeToolbar from '$lib/components/builder/panels/NodeToolbar.svelte';
  import NodeEditor from '$lib/components/builder/panels/NodeEditor.svelte';
  import { createFlowBuilderStore } from '$lib/stores/flowBuilder.svelte';
  import { FlowsService } from '$lib/services/flows.service';
  import { SaveFlowRequest } from '$lib/dto/flows/requests';
  import type { NodeType } from '$lib/dto/flows/types';

  const store = createFlowBuilderStore();
  const service = new FlowsService();
  let saving = $state(false);
  let toast = $state('');
  let showCsvUpload = $state(false);
  let csvPreviewRows = $state<string[][]>([]);
  let csvError = $state('');
  let dragOver = $state(false);
  let showAgentModal = $state(false);
  let agentInfo = $state<{ model: string; instructions: string; output_schema: Record<string, any> } | null>(null);

  // Nomes dos produtos do CSV, para autocomplete no NodeEditor
  let catalogItems = $derived.by(() => {
    if (!store.pricingCsv) return [];
    const { rows, valid } = parseCsv(store.pricingCsv);
    if (!valid || rows.length < 2) return [];
    const header = rows[0];
    const idx = header.indexOf('produto');
    if (idx === -1) return [];
    return rows.slice(1).map(r => r[idx]).filter(Boolean);
  });
  let agentLoading = $state(false);

  async function openAgentModal() {
    showAgentModal = true;
    if (agentInfo) return;
    agentLoading = true;
    try {
      const res = await authFetch('/api/agent-info');
      if (res.ok) {
        agentInfo = await res.json();
      }
    } catch {
      // silently fail
    } finally {
      agentLoading = false;
    }
  }

  const CSV_TEMPLATE = `produto,preco,unidade,categoria
Borne 16A Level 1,499,unidade,borne
Borne 32A Level 2,699,unidade,borne
Borne 40A Level 2,899,unidade,borne
Borne 48A Level 2,1099,unidade,borne
Controller DCC-9,699,unidade,accessoire
Installation murale exterieure,490,unidade,installation
Installation sur poteau,690,unidade,installation
Cablage par pied,9,pied,cablage
Deplacement,69,unidade,deplacement
Mise a niveau panneau 100A vers 200A,1800,unidade,upgrade
Sous-panneau 100A,900,unidade,upgrade
Subvention Roulez Vert (Level 2),-600,unidade,rabais`;

  /**
   * Normaliza número em qualquer formato para float válido.
   * Aceita: 1099 | 1099.50 | 1099,50 | 1.099,50 | 1,099.50
   */
  function normalizeNumber(val: string): string {
    val = val.trim();
    if (!val) return '0';

    const hasComma = val.includes(',');
    const hasDot = val.includes('.');

    if (hasComma && hasDot) {
      // 1.099,50 (BR/FR) or 1,099.50 (US)
      const lastComma = val.lastIndexOf(',');
      const lastDot = val.lastIndexOf('.');
      if (lastComma > lastDot) {
        // 1.099,50 → comma is decimal
        return val.replace(/\./g, '').replace(',', '.');
      } else {
        // 1,099.50 → dot is decimal
        return val.replace(/,/g, '');
      }
    } else if (hasComma) {
      // 1099,50 → comma is decimal
      return val.replace(',', '.');
    }
    // 1099 or 1099.50 → already fine
    return val;
  }

  function parseCsv(text: string): { rows: string[][]; valid: boolean; error: string } {
    const lines = text.trim().split('\n').map(l => l.trim()).filter(l => l);
    if (lines.length < 2) return { rows: [], valid: false, error: 'Le CSV doit avoir au moins un en-tête et une ligne de données' };

    // Auto-detect separator: ; or ,
    const sep = lines[0].includes(';') ? ';' : ',';
    const header = lines[0].split(sep).map(h => h.trim().toLowerCase());
    const requiredCols = ['produto', 'preco'];
    const missing = requiredCols.filter(c => !header.includes(c));
    if (missing.length > 0) return { rows: [], valid: false, error: `Colonnes manquantes: ${missing.join(', ')}. Format requis: produto,preco,unidade,categoria` };

    const rows = lines.map(l => l.split(sep).map(c => c.trim()));

    // Validate and normalize preco (skip header)
    const precoIdx = header.indexOf('preco');
    for (let i = 1; i < rows.length; i++) {
      const raw = rows[i][precoIdx];
      const normalized = normalizeNumber(raw);
      if (raw && isNaN(parseFloat(normalized))) {
        return { rows: [], valid: false, error: `Ligne ${i + 1}: "${raw}" n'est pas un prix valide` };
      }
      rows[i][precoIdx] = normalized;
    }

    return { rows, valid: true, error: '' };
  }

  function handleCsvFile(file: File) {
    csvError = '';
    csvPreviewRows = [];
    if (!file.name.endsWith('.csv')) {
      csvError = 'Seuls les fichiers .csv sont acceptés';
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const { rows, valid, error } = parseCsv(text);
      if (!valid) {
        csvError = error;
        return;
      }
      csvPreviewRows = rows;
      // Normalize: convert ; separator to , for storage
      store.pricingCsv = text.includes(';') ? text.replace(/;/g, ',') : text;
    };
    reader.readAsText(file);
  }

  function downloadTemplate() {
    const blob = new Blob([CSV_TEMPLATE], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'modele_prix.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  function openCsvModal() {
    showCsvUpload = true;
    csvError = '';
    // If there's already a CSV loaded, parse it for preview
    if (store.pricingCsv) {
      const { rows } = parseCsv(store.pricingCsv);
      csvPreviewRows = rows;
    } else {
      csvPreviewRows = [];
    }
  }

  const nodeTypes: NodeTypes = {
    start: StartNode as any,
    question: QuestionNode as any,
    message: MessageNode as any,
    end: EndNode as any
  };

  const selectedNode = $derived(
    store.selectedNodeId ? store.nodes.find(n => n.id === store.selectedNodeId) : null
  );

  onMount(async () => {
    const id = page.params.id;
    if (id && id !== 'new') {
      const flow = await service.getById(id);
      if (flow) {
        store.loadFlow(flow);
        return;
      }
    }
    // New flow — add start node
    store.addNode('start', { x: 300, y: 50 });
    store.hasChanges = false;
  });

  let flowInstance: any = null;

  function handleAddNode(type: NodeType) {
    // Place new node below the selected node, or below the last one
    let refNode = selectedNode;
    if (!refNode && store.nodes.length > 0) {
      refNode = store.nodes.reduce((a, b) => a.position.y > b.position.y ? a : b);
    }
    const x = refNode ? refNode.position.x : 300;
    const y = refNode ? refNode.position.y + 180 : 50;
    store.addNode(type, { x, y });
    // Fit view to show all nodes
    setTimeout(() => flowInstance?.fitView({ duration: 300, padding: 0.2 }), 50);
  }

  function handleConnect(connection: Connection) {
    store.addEdge({
      id: '',
      source: connection.source!,
      target: connection.target!,
      sourceHandle: connection.sourceHandle || undefined,
      animated: true
    } as Edge);
  }

  function handleNodeClick({ node: clickedNode }: { node: Node }) {
    store.selectedNodeId = clickedNode.id;
  }

  function handlePaneClick() {
    store.selectedNodeId = null;
  }

  async function handleSave() {
    saving = true;
    toast = '';
    try {
      const flowData = store.getFlowData();
      const dto = new SaveFlowRequest({
        _id: store.flowId,
        name: store.flowName,
        nodes: flowData.nodes,
        edges: flowData.edges,
        status: 'draft',
        pricing_csv: store.pricingCsv
      });
      const saved = await service.save(dto);
      if (saved?._id && !store.flowId) {
        store.flowId = saved._id;
      }
      store.hasChanges = false;
      toast = 'Salvo!';
      setTimeout(() => goto('/admin/flows'), 1000);
    } catch (e: any) {
      toast = 'Erro: ' + e.message;
    } finally {
      saving = false;
    }
  }
</script>

<div class="h-screen flex flex-col bg-gray-50">
  <!-- Header -->
  <header class="bg-white border-b border-gray-200 px-4 py-2.5 flex items-center justify-between z-10">
    <div class="flex items-center gap-3">
      <button onclick={() => goto('/admin/scheduling')} class="text-gray-400 hover:text-gray-700 cursor-pointer transition-colors p-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
        </svg>
      </button>
      <div class="h-5 w-px bg-gray-200"></div>
      <input
        type="text"
        bind:value={store.flowName}
        class="text-base font-semibold text-gray-900 bg-transparent border-b-2 border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5 transition-colors"
      />
    </div>
    <div class="flex items-center gap-2">
      {#if toast}
        <span class="text-xs font-medium px-2.5 py-1 rounded-full {toast.startsWith('Erro') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'} transition-all">
          {toast}
        </span>
      {/if}
      {#if store.hasChanges}
        <span class="w-2 h-2 rounded-full bg-yellow-400" title="Alterações não salvas"></span>
      {/if}
      {#if store.flowId}
        <button
          onclick={() => goto(`/admin/flows/${store.flowId}/preview`)}
          class="text-xs font-medium text-purple-600 hover:text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-md px-3 py-1.5 cursor-pointer transition-colors flex items-center gap-1"
          title="Visualizar questionário"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Preview
        </button>
      {/if}
      <button
        onclick={handleSave}
        disabled={saving}
        class="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 cursor-pointer transition-colors"
      >
        {saving ? 'Salvando...' : 'Salvar'}
      </button>
    </div>
  </header>

  <!-- Toolbar -->
  <div class="px-4 py-2 z-10">
    <NodeToolbar onAddNode={handleAddNode} />
  </div>

  <!-- Canvas + Editor Panel -->
  <div class="flex-1 flex overflow-hidden">
    <div class="flex-1">
      <SvelteFlow
        bind:nodes={store.nodes}
        bind:edges={store.edges}
        {nodeTypes}
        onconnect={handleConnect}
        onnodeclick={handleNodeClick}
        onpaneclick={handlePaneClick}
        onnodesdelete={(nodes) => nodes.forEach(n => store.removeNode(n.id))}
        onedgesdelete={(edges) => edges.forEach(e => store.removeEdge(e.id))}
        oninit={(instance) => flowInstance = instance}
        deleteKey={['Backspace', 'Delete']}
        fitView
        colorMode="light"
        connectionMode="loose"
      >
        <Controls position="bottom-left" />
        <MiniMap position="bottom-right" />
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} />
      </SvelteFlow>
    </div>

    {#if selectedNode}
      <NodeEditor
        node={selectedNode}
        onUpdate={(data) => store.updateNodeData(selectedNode.id, data)}
        onDelete={() => store.removeNode(selectedNode.id)}
        onClose={() => store.selectedNodeId = null}
        {catalogItems}
      />
    {/if}
  </div>
</div>

<!-- Modal: Upload CSV de preços -->
{#if showCsvUpload}
  <div class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col">
      <div class="px-6 py-4 border-b flex items-center justify-between">
        <div>
          <h2 class="text-base font-bold text-gray-900">Catalogue de prix (CSV)</h2>
          <p class="text-xs text-gray-500 mt-0.5">Envoyez votre fichier CSV avec les produits et prix. L'IA utilisera ce catalogue pour generer les devis.</p>
        </div>
        <button onclick={() => showCsvUpload = false} class="text-gray-400 hover:text-gray-600 cursor-pointer p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="p-6 overflow-y-auto flex-1 space-y-4">
        <!-- Download template -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
            <span class="text-sm text-blue-700">Telechargez le modele CSV pour voir le format attendu</span>
          </div>
          <button
            onclick={downloadTemplate}
            class="text-xs font-semibold text-blue-700 bg-blue-100 hover:bg-blue-200 px-3 py-1.5 rounded-md cursor-pointer transition-colors"
          >
            Telecharger modele
          </button>
        </div>

        <!-- Drop zone -->
        <div
          class="border-2 border-dashed rounded-xl p-8 text-center transition-colors {dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}"
          ondragover={(e) => { e.preventDefault(); dragOver = true; }}
          ondragleave={() => dragOver = false}
          ondrop={(e) => { e.preventDefault(); dragOver = false; const f = e.dataTransfer?.files[0]; if (f) handleCsvFile(f); }}
        >
          <svg class="w-10 h-10 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
          </svg>
          <p class="text-sm text-gray-600 font-medium mb-1">Glissez votre fichier CSV ici</p>
          <p class="text-xs text-gray-400 mb-3">ou</p>
          <label class="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 cursor-pointer transition-colors">
            Choisir un fichier
            <input type="file" accept=".csv" class="hidden" onchange={(e) => { const f = (e.target as HTMLInputElement).files?.[0]; if (f) handleCsvFile(f); }} />
          </label>
          <p class="text-xs text-gray-400 mt-2">Format: produto,preco,unidade,categoria</p>
        </div>

        <!-- Error -->
        {#if csvError}
          <div class="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
            <svg class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
            <p class="text-sm text-red-700">{csvError}</p>
          </div>
        {/if}

        <!-- Preview table -->
        {#if csvPreviewRows.length > 0}
          <div>
            <h3 class="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">Apercu du catalogue ({csvPreviewRows.length - 1} produits)</h3>
            <div class="border border-gray-200 rounded-lg overflow-hidden">
              <table class="w-full text-sm">
                <thead>
                  <tr class="bg-gray-50">
                    {#each csvPreviewRows[0] as header}
                      <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase">{header}</th>
                    {/each}
                  </tr>
                </thead>
                <tbody>
                  {#each csvPreviewRows.slice(1) as row, i}
                    <tr class="{i % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}">
                      {#each row as cell, j}
                        <td class="px-3 py-1.5 text-xs {j === 1 ? 'font-mono font-semibold text-green-700' : 'text-gray-700'}">{j === 1 && !cell.startsWith('-') ? `$${cell}` : j === 1 ? `-$${cell.replace('-','')}` : cell}</td>
                      {/each}
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </div>
        {/if}
      </div>

      <div class="px-6 py-3 border-t flex justify-between items-center">
        <div>
          {#if store.pricingCsv && csvPreviewRows.length === 0}
            <span class="text-xs text-green-600 font-medium">CSV deja charge</span>
          {/if}
        </div>
        <div class="flex gap-2">
          {#if store.pricingCsv}
            <button
              onclick={() => { store.pricingCsv = ''; csvPreviewRows = []; toast = 'CSV supprime'; setTimeout(() => toast = '', 2500); }}
              class="text-xs text-red-600 px-3 py-2 rounded-lg hover:bg-red-50 cursor-pointer transition-colors"
            >
              Supprimer CSV
            </button>
          {/if}
          <button
            onclick={() => showCsvUpload = false}
            class="text-sm font-medium text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- Modal: Agente IA (somente leitura) -->
{#if showAgentModal}
  <div class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col">
      <div class="px-6 py-4 border-b flex items-center justify-between">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
          <div>
            <h2 class="text-base font-bold text-gray-900">Agente IA</h2>
            <p class="text-xs text-gray-500">Configuration en lecture seule</p>
          </div>
        </div>
        <button onclick={() => showAgentModal = false} class="text-gray-400 hover:text-gray-600 cursor-pointer p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="p-6 overflow-y-auto flex-1 space-y-5">
        {#if agentLoading}
          <div class="text-center py-8 text-gray-400">Chargement...</div>
        {:else if agentInfo}
          <!-- Modelo -->
          <div>
            <label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Modele</label>
            <div class="mt-1 bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 font-mono text-sm text-indigo-700">
              {agentInfo.model}
            </div>
          </div>

          <!-- Prompt / Instructions -->
          <div>
            <label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Prompt (Instructions systeme)</label>
            <div class="mt-1 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto">
              {agentInfo.instructions}
            </div>
          </div>

          <!-- Output Schema -->
          <div>
            <label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Schema de sortie (Output parsing)</label>
            <div class="mt-1 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 font-mono text-xs text-gray-600 whitespace-pre-wrap max-h-60 overflow-y-auto">
              {JSON.stringify(agentInfo.output_schema, null, 2)}
            </div>
          </div>

          <!-- Info box -->
          <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-3 flex gap-2">
            <svg class="w-4 h-4 text-indigo-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
            <p class="text-xs text-indigo-700">
              Ce sont les parametres actuels de l'agent IA. Le prompt inclut aussi le catalogue CSV et les reponses du client au moment de la generation.
              Un validateur verifie chaque item contre le catalogue et corrige les prix automatiquement.
            </p>
          </div>
        {:else}
          <div class="text-center py-8 text-red-400">Impossible de charger les informations de l'agent. Verifiez que le backend est demarre.</div>
        {/if}
      </div>

      <div class="px-6 py-3 border-t flex justify-end">
        <button
          onclick={() => showAgentModal = false}
          class="text-sm font-medium text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
        >
          Fermer
        </button>
      </div>
    </div>
  </div>
{/if}
