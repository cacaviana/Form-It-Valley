import type { Flow } from '$lib/dto/flows/types';
import { authFetch } from '$lib/utils/auth-fetch';

export class FlowsRepository {
  async list(): Promise<Flow[]> {
    const res = await authFetch('/api/flows');
    if (!res.ok) throw new Error('Erro ao listar fluxos');
    const data = await res.json();
    return data.flows || data;
  }

  async getById(id: string): Promise<Flow | null> {
    const res = await authFetch(`/api/flows/${id}`);
    if (!res.ok) throw new Error('Erro ao buscar fluxo');
    return res.json();
  }

  async getBySlug(slug: string): Promise<Flow | null> {
    const res = await fetch(`/api/flows/slug/${slug}`);
    if (!res.ok) throw new Error('Erro ao buscar fluxo');
    return res.json();
  }

  async save(payload: Record<string, unknown>): Promise<Flow> {
    const method = payload._id ? 'PUT' : 'POST';
    const url = payload._id ? `/api/flows/${payload._id}` : '/api/flows';
    const res = await authFetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao salvar fluxo');
    return res.json();
  }
}
