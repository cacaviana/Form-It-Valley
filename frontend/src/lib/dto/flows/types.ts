export type NodeType = 'start' | 'question' | 'message' | 'end' | 'blacklist';

export type QuestionType =
  | 'single_choice'
  | 'yes_no'
  | 'number'
  | 'text'
  | 'multiple_choice'
  | 'date'
  | 'dropdown'
  | 'photo';

export interface FlowOption {
  id: string;
  label: string;
  value: string;
  catalogProduct?: string; // Nome exato do produto no CSV (opcional, para match determinístico)
}

export interface FlowNodeData {
  title: string;
  // Question node
  questionType?: QuestionType;
  options?: FlowOption[];
  required?: boolean;
  tooltip?: string;
  imageUrl?: string;
  // For rating
  ratingMax?: number;
  // For rating/number — associates the numeric answer as quantity for a catalog product
  quantityProduct?: string;
  // For dropdown
  dropdownPlaceholder?: string;
  // Start node
  collectFields?: string[];
  // Message node
  message?: string;
  isSpecialist?: boolean;
  // End node
  endType?: 'scheduling' | 'finish';
  businessContext?: string;
  aiInstruction?: string;
  outputFormat?: 'pdf' | 'txt' | 'both';
  // WhatsApp template config (scheduling)
  whatsappTemplate?: string;
  whatsappVariables?: string[]; // cada variavel pode usar placeholders: {{nome}}, {{data}}, {{horario}}, {{link}}
  // ActiveCampaign
  activecampaignListId?: string;
  activecampaignListName?: string;
  // Blacklist node
  blockedMessage?: string;
  blacklistTotalEntries?: number;
  blacklistUploadedAt?: string;
}

export interface FlowNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: FlowNodeData;
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  label?: string;
}

export type PageTemplate = 'centered' | 'pos_ia' | 'pos_dados';

export interface SchedulingDateEntry {
  date: string;     // 'YYYY-MM-DD'
  times: string[];  // ['09:00', '14:30', ...]
}

export interface SchedulingConfig {
  dates: SchedulingDateEntry[];
  max_bookings_per_slot: number;
}

export interface PageContent {
  topBannerText?: string;
  headline?: string;
  headlineHighlight?: string;
  bullets?: string[];
  disciplinesTitle?: string;
  disciplines?: string[];
}

export interface Flow {
  _id?: string;
  tenant_id: string;
  name: string;
  slug: string;
  status: 'draft' | 'published' | 'archived';
  version: number;
  nodes: FlowNode[];
  edges: FlowEdge[];
  pricing_csv?: string;
  activecampaign_list_id?: string;
  activecampaign_list_name?: string;
  theme_color?: string;
  page_template?: PageTemplate;
  page_content?: PageContent;
  scheduling_config?: SchedulingConfig | null;
  meeting_link_override?: string | null;
  created_at?: string;
  updated_at?: string;
}
