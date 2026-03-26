export type NodeType = 'start' | 'question' | 'message' | 'end';

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
  endType?: 'quote' | 'specialist' | 'thank_you' | 'scheduling';
  businessContext?: string;
  aiInstruction?: string;
  outputFormat?: 'pdf' | 'txt' | 'both';
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
  created_at?: string;
  updated_at?: string;
}
