import { SubmissionsRepository } from '$lib/data/repositories/submissions.repository';
import type { SubmissionPayload } from '$lib/data/repositories/submissions.repository';

export class SubmissionsService {
  private repo = new SubmissionsRepository();

  async submit(payload: SubmissionPayload) {
    return await this.repo.create(payload);
  }
}
