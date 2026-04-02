import type { FlowNode, FlowEdge } from './types';

export class SaveFlowRequest {
  private _id: string | null;
  private name: string;
  private slug: string;
  private nodes: FlowNode[];
  private edges: FlowEdge[];
  private status: string;
  private pricing_csv: string;
  private activecampaign_list_id: string;
  private activecampaign_list_name: string;
  private theme_color: string;

  constructor(data: { _id?: string | null; name: string; slug?: string; nodes: FlowNode[]; edges: FlowEdge[]; status?: string; pricing_csv?: string; activecampaign_list_id?: string; activecampaign_list_name?: string; theme_color?: string }) {
    this._id = data._id || null;
    this.name = data.name || '';
    this.slug = data.slug || data.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
    this.nodes = data.nodes || [];
    this.edges = data.edges || [];
    this.status = data.status || 'draft';
    this.pricing_csv = data.pricing_csv || '';
    this.activecampaign_list_id = data.activecampaign_list_id || '';
    this.activecampaign_list_name = data.activecampaign_list_name || '';
    this.theme_color = data.theme_color || 'violet';
    if (!this.name.trim()) throw new Error('Nome do fluxo é obrigatório');
  }

  isValid(): boolean {
    return this.name.trim() !== '' && this.nodes.length > 0;
  }

  toPayload(): Record<string, unknown> {
    const payload: Record<string, unknown> = {
      name: this.name,
      slug: this.slug,
      nodes: this.nodes,
      edges: this.edges,
      status: this.status,
      pricing_csv: this.pricing_csv,
      activecampaign_list_id: this.activecampaign_list_id || '',
      activecampaign_list_name: this.activecampaign_list_name || '',
      theme_color: this.theme_color || 'violet'
    };
    if (this._id) payload._id = this._id;
    return payload;
  }

  getName() { return this.name; }
  getSlug() { return this.slug; }
}
