
import { api } from "./api";
import type { SystemStatus } from "../types/dashboard.types";

export const getSystemStatus = async (): Promise<SystemStatus> => {
  const { data } = await api.get<SystemStatus>("/dashboard/status");
  return data;
};