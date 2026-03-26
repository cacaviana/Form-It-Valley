import type { FlowNode, FlowEdge, NodeType, FlowNodeData } from '$lib/dto/flows/types';
import type { Node, Edge } from '@xyflow/svelte';

function generateId() {
  return 'node_' + crypto.randomUUID().slice(0, 8);
}

export function toSvelteFlowNodes(flowNodes: FlowNode[]): Node[] {
  return flowNodes.map(n => ({
    id: n.id,
    type: n.type,
    position: n.position,
    data: n.data
  }));
}

export function toSvelteFlowEdges(flowEdges: FlowEdge[]): Edge[] {
  return flowEdges.map(e => ({
    id: e.id,
    source: e.source,
    target: e.target,
    sourceHandle: e.sourceHandle,
    label: e.label,
    animated: true
  }));
}

const defaultDataByType: Record<NodeType, () => FlowNodeData> = {
  start: () => ({
    title: 'Início',
    collectFields: ['name', 'email', 'phone', 'address']
  }),
  question: () => ({
    title: 'Nova Pergunta',
    questionType: 'single_choice',
    options: [
      { id: 'opt_' + crypto.randomUUID().slice(0, 6), label: 'Opção 1', value: 'opcao_1' },
      { id: 'opt_' + crypto.randomUUID().slice(0, 6), label: 'Opção 2', value: 'opcao_2' }
    ],
    required: true
  }),
  message: () => ({
    title: 'Mensagem',
    message: 'Texto informativo para o cliente.',
    isSpecialist: false
  }),
  end: () => ({
    title: 'Fim',
    endType: 'quote',
    businessContext: '',
    aiInstruction: '',
    outputFormat: 'pdf'
  })
};

export function createFlowBuilderStore() {
  let nodes = $state.raw<Node[]>([]);
  let edges = $state.raw<Edge[]>([]);
  let flowName = $state('Novo Fluxo');
  let flowId = $state<string | null>(null);
  let pricingCsv = $state('');
  let selectedNodeId = $state<string | null>(null);
  let hasChanges = $state(false);

  function loadFlow(flow: { _id?: string; name: string; nodes: FlowNode[]; edges: FlowEdge[]; pricing_csv?: string }) {
    flowId = flow._id || null;
    flowName = flow.name;
    pricingCsv = flow.pricing_csv || '';
    nodes = toSvelteFlowNodes(flow.nodes);
    edges = toSvelteFlowEdges(flow.edges);
    hasChanges = false;
  }

  function addNode(type: NodeType, position: { x: number; y: number }) {
    const id = generateId();
    const newNode: Node = {
      id,
      type,
      position,
      data: defaultDataByType[type]()
    };
    nodes = [...nodes, newNode];
    hasChanges = true;
    selectedNodeId = id;
  }

  function updateNodeData(nodeId: string, data: Partial<FlowNodeData>) {
    nodes = nodes.map(n =>
      n.id === nodeId ? { ...n, data: { ...n.data, ...data } } : n
    );
    hasChanges = true;
  }

  function removeNode(nodeId: string) {
    nodes = nodes.filter(n => n.id !== nodeId);
    edges = edges.filter(e => e.source !== nodeId && e.target !== nodeId);
    if (selectedNodeId === nodeId) selectedNodeId = null;
    hasChanges = true;
  }

  function addEdge(edge: Edge) {
    const exists = edges.some(
      e => e.source === edge.source && e.target === edge.target && e.sourceHandle === edge.sourceHandle
    );
    if (exists) return;
    edges = [...edges, { ...edge, id: 'e_' + crypto.randomUUID().slice(0, 8), animated: true }];
    hasChanges = true;
  }

  function removeEdge(edgeId: string) {
    edges = edges.filter(e => e.id !== edgeId);
    hasChanges = true;
  }

  function getFlowData(): { nodes: FlowNode[]; edges: FlowEdge[] } {
    return {
      nodes: nodes.map(n => ({
        id: n.id,
        type: n.type as NodeType,
        position: n.position,
        data: n.data as FlowNodeData
      })),
      edges: edges.map(e => ({
        id: e.id,
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle,
        label: e.label as string | undefined
      }))
    };
  }

  return {
    get nodes() { return nodes; },
    set nodes(v: Node[]) { nodes = v; hasChanges = true; },
    get edges() { return edges; },
    set edges(v: Edge[]) { edges = v; hasChanges = true; },
    get flowName() { return flowName; },
    set flowName(v: string) { flowName = v; hasChanges = true; },
    get flowId() { return flowId; },
    set flowId(v: string | null) { flowId = v; },
    get pricingCsv() { return pricingCsv; },
    set pricingCsv(v: string) { pricingCsv = v; hasChanges = true; },
    get selectedNodeId() { return selectedNodeId; },
    set selectedNodeId(v: string | null) { selectedNodeId = v; },
    get hasChanges() { return hasChanges; },
    set hasChanges(v: boolean) { hasChanges = v; },
    loadFlow,
    addNode,
    updateNodeData,
    removeNode,
    addEdge,
    removeEdge,
    getFlowData
  };
}
