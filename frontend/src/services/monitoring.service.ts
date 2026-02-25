
import { api } from "./api";
import type { ApiOk } from "../types/api.types";
import type { MonitorJob, StartJobInput, StartJobResponse } from "../types/monitoring.types";

function unwrap<T>(payload: ApiOk<T>): T {
  return payload.data;
}

export const monitoringService = {
  async listJobs(): Promise<MonitorJob[]> {
    const { data } = await api.get<ApiOk<MonitorJob[]>>("/monitoring/jobs");
    return unwrap(data);
  },

  async startJob(input: StartJobInput): Promise<StartJobResponse> {
    const { data } = await api.post<ApiOk<StartJobResponse>>("/monitoring/jobs", input);
    return unwrap(data);
  },

  async getJob(jobId: string): Promise<MonitorJob> {
    const { data } = await api.get<ApiOk<MonitorJob>>(`/monitoring/jobs/${jobId}`);
    return unwrap(data);
  },

  async stopJob(jobId: string): Promise<{ job_id: string; status: string }> {
    const { data } = await api.post<ApiOk<{ job_id: string; status: string }>>(
      `/monitoring/jobs/${jobId}/stop`,
      {}
    );
    return unwrap(data);
  },
};