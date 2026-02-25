export type MonitorJobStatus = "running" | "stopped" | "completed" | "error";

export interface Reservation {
  at: string;
  event_id: number;
  sector_id: number;
  sector_name: string;
  price: string;
  cart_total: number;
}

export interface MonitorJob {
  id: string;
  account_id: string;
  event_id: number;
  sector_ids: number[];
  status: MonitorJobStatus;

  created_at: string;
  started_at: string;
  stopped_at?: string | null;

  poll_interval_seconds: number;
  max_cart_tickets: number;

  last_poll_at?: string | null;
  last_message?: string | null;
  error?: string | null;

  cart_total: number;
  reservations: Reservation[];
}

export interface StartJobInput {
  account_id: string;
  event_id: number;
  sector_ids?: number[];
  poll_interval_seconds?: number;
  max_cart_tickets?: number;
}

export interface StartJobResponse {
  job_id: string;
}