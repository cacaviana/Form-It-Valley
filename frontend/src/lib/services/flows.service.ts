import { FlowsRepository } from '$lib/data/repositories/flows.repository';
import type { SaveFlowRequest } from '$lib/dto/flows/requests';

export class FlowsService {
  private repo = new FlowsRepository();

  async list() {
    return await this.repo.list();
  }

  async getById(id: string) {
    return await this.repo.getById(id);
  }

  async getBySlug(slug: string) {
    return await this.repo.getBySlug(slug);
  }

  async save(dto: SaveFlowRequest) {
    if (!dto.isValid()) throw new Error('Dados do fluxo inválidos');
    return await this.repo.save(dto.toPayload());
  }
}
