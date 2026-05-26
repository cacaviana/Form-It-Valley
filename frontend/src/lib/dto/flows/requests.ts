import type { FlowNode, FlowEdge, PageTemplate, PageContent, SchedulingConfig, EmailConfig, UITexts } from './types';

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
  private page_template: PageTemplate;
  private page_content: PageContent;
  private scheduling_config: SchedulingConfig | null;
  private meeting_link_override: string | null;
  private gcal_event_title: string | null;
  private email_config: EmailConfig | null;
  private ui_texts: UITexts | null;

  constructor(data: { _id?: string | null; name: string; slug?: string; nodes: FlowNode[]; edges: FlowEdge[]; status?: string; pricing_csv?: string; activecampaign_list_id?: string; activecampaign_list_name?: string; theme_color?: string; page_template?: PageTemplate; page_content?: PageContent; scheduling_config?: SchedulingConfig | null; meeting_link_override?: string | null; gcal_event_title?: string | null; email_config?: EmailConfig | null; ui_texts?: UITexts | null }) {
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
    this.page_template = data.page_template || 'centered';
    this.page_content = data.page_content || {};
    this.scheduling_config = data.scheduling_config ?? null;
    this.meeting_link_override = data.meeting_link_override?.trim() || null;
    this.gcal_event_title = data.gcal_event_title?.trim() || null;
    this.email_config = data.email_config ?? null;
    this.ui_texts = data.ui_texts ?? null;
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
      theme_color: this.theme_color || 'violet',
      page_template: this.page_template || 'centered',
      page_content: this.page_content || {},
      scheduling_config: this.scheduling_config,
      meeting_link_override: this.meeting_link_override,
      gcal_event_title: this.gcal_event_title,
      email_config: this.email_config,
      ui_texts: this.ui_texts
    };
    if (this._id) payload._id = this._id;
    return payload;
  }

  getName() { return this.name; }
  getSlug() { return this.slug; }
}
