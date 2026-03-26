export interface SubmissionPayload {
  flow_id: string;
  flow_slug: string;
  client_name: string;
  client_email: string;
  client_phone?: string;
  client_address?: string;
  answers: { node_id: string; question: string; value: string }[];
  end_node_id: string;
}

export interface SubmissionResult {
  id: string;
  flow_id: string;
  flow_slug: string;
  client_name: string;
  client_email: string;
  end_type: string;
  quote_text: string | null;
  status: string;
  created_at: string;
}

export class SubmissionsRepository {
  async create(payload: SubmissionPayload): Promise<SubmissionResult> {
    const res = await fetch('/api/submissions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao enviar submission');
    return res.json();
  }
}
