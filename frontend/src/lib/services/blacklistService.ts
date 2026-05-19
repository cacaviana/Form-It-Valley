import { authFetch } from '$lib/utils/auth-fetch';

export interface BlacklistMetadata {
  exists: boolean;
  total_entries: number;
  csv_uploaded_at?: string;
  csv_uploaded_by?: string | null;
}

export interface UploadResult {
  blacklist_id: string;
  total_entries: number;
  skipped_lines: number;
  errors: string[];
  csv_uploaded_at: string;
}

export async function getBlacklistMetadata(flowId: string): Promise<BlacklistMetadata> {
  const res = await authFetch(`/api/blacklist/by-flow/${encodeURIComponent(flowId)}`);
  if (!res.ok) return { exists: false, total_entries: 0 };
  return res.json();
}

export async function uploadBlacklistCsv(flowId: string, file: File): Promise<UploadResult> {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('scope_id', flowId);
  fd.append('scope_type', 'flow');
  const res = await authFetch('/api/blacklist/upload', { method: 'POST', body: fd });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err?.detail;
    const msg = typeof detail === 'string'
      ? detail
      : detail?.message
      ? `${detail.message}: ${(detail.errors || []).join('; ')}`
      : 'Erro ao fazer upload';
    throw new Error(msg);
  }
  return res.json();
}

export async function deleteBlacklist(flowId: string): Promise<void> {
  const res = await authFetch(`/api/blacklist/by-flow/${encodeURIComponent(flowId)}`, { method: 'DELETE' });
  if (!res.ok && res.status !== 404) {
    throw new Error('Erro ao excluir');
  }
}

export interface BlacklistEntry {
  email: string | null;
  phone: string | null;
}

export async function listEntries(flowId: string): Promise<BlacklistEntry[]> {
  const res = await authFetch(`/api/blacklist/by-flow/${encodeURIComponent(flowId)}/entries`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.entries || [];
}

export async function addEntry(
  flowId: string,
  payload: { email?: string; ddi?: string; ddd?: string; numero?: string }
): Promise<{ total_entries: number }> {
  const res = await authFetch(`/api/blacklist/by-flow/${encodeURIComponent(flowId)}/entries`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || 'Erro ao adicionar');
  }
  return res.json();
}

export async function removeEntry(
  flowId: string,
  payload: { email?: string | null; phone?: string | null }
): Promise<{ total_entries: number }> {
  const res = await authFetch(`/api/blacklist/by-flow/${encodeURIComponent(flowId)}/entries`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || 'Erro ao excluir');
  }
  return res.json();
}

export async function checkLead(payload: {
  flow_id: string;
  email?: string;
  ddi?: string;
  ddd?: string;
  numero?: string;
}): Promise<{ blocked: boolean; matched_field?: string }> {
  const res = await fetch('/api/public/blacklist/check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) return { blocked: false };
  return res.json();
}
