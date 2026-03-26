import type { Flow } from './types';

export class FlowResponse {
  private data: Flow;

  constructor(raw: Record<string, unknown>) {
    this.data = raw as unknown as Flow;
  }

  getId() { return this.data._id; }
  getName() { return this.data.name; }
  getSlug() { return this.data.slug; }
  getStatus() { return this.data.status; }
  getNodes() { return this.data.nodes; }
  getEdges() { return this.data.edges; }
  getVersion() { return this.data.version; }
  toRaw() { return this.data; }
}
