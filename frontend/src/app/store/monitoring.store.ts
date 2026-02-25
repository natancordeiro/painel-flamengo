
import { create } from "zustand";
import type { MonitorJob } from "../../types/monitoring.types";

export interface TicketItem {
  id: string;
  match: string;
  setor: string;
  competition: string;
  location: string;
  price: string;
  type: string;
}

export interface TicketRealtime {
  match: string;
  setor: string;
  quantity: number;
  datetime: string;
}

interface MonitoringState {
  active: boolean;


  activeJobId: string | null;
  job: MonitorJob | null;
  jobs: MonitorJob[];

  tickets: TicketItem[];

  loading: boolean;
  lastError: string | null;


  lastTicket: TicketRealtime | null;
  alertOpen: boolean;

  setActive: (v: boolean) => void;

  setActiveJobId: (jobId: string | null) => void;
  setJob: (job: MonitorJob | null) => void;
  setJobs: (jobs: MonitorJob[]) => void;

  setLoading: (v: boolean) => void;
  setError: (msg: string | null) => void;

  setTickets: (tickets: TicketItem[]) => void;
  clearTickets: () => void;


  addRealtimeTicket: (ticket: TicketRealtime) => void;
  closeAlert: () => void;

  clear: () => void;
}

const MAX_TICKETS = 40;

function safeIsoToMs(value?: string | null): number {
  if (!value) return 0;
  const ms = Date.parse(value);
  return Number.isFinite(ms) ? ms : 0;
}


function jobToTickets(job: MonitorJob | null): TicketItem[] {
  if (!job) return [];

  const reservations = Array.isArray(job.reservations) ? job.reservations : [];


  const sorted = [...reservations].sort(
    (a, b) => safeIsoToMs(b.at) - safeIsoToMs(a.at)
  );

  return sorted.slice(0, MAX_TICKETS).map((r) => ({
    id: `${r.at}-${r.sector_id}-${r.cart_total}`,
    match: `Event #${r.event_id}`,
    setor: r.sector_name || String(r.sector_id),
    competition: "Evento",
    location: "",
    price: r.price ? `R$ ${r.price}` : "",
    type: `Carrinho: ${r.cart_total}`,
  }));
}

export const useMonitoringStore = create<MonitoringState>((set) => ({
  active: false,

  activeJobId: null,
  job: null,
  jobs: [],

  tickets: [],

  loading: false,
  lastError: null,

  lastTicket: null,
  alertOpen: false,

  setActive: (v) => set({ active: v }),

  setActiveJobId: (jobId) => set({ activeJobId: jobId }),

  setJob: (job) =>
    set({
      job,
      tickets: jobToTickets(job),
    }),

  setJobs: (jobs) => set({ jobs }),

  setLoading: (v) => set({ loading: v }),
  setError: (msg) => set({ lastError: msg }),

  setTickets: (tickets) => set({ tickets: tickets.slice(0, MAX_TICKETS) }),
  clearTickets: () => set({ tickets: [] }),

  addRealtimeTicket: (ticket) =>
    set((state) => ({
      lastTicket: ticket,
      alertOpen: true,
      tickets: [
        {
          id: crypto.randomUUID(),
          match: ticket.match,
          setor: ticket.setor,
          competition: "Evento",
          location: "",
          price: "",
          type: "Realtime",
        },
        ...state.tickets,
      ].slice(0, MAX_TICKETS),
    })),

  closeAlert: () => set({ alertOpen: false }),

  clear: () =>
    set({
      active: false,
      activeJobId: null,
      job: null,
      jobs: [],
      tickets: [],
      loading: false,
      lastError: null,
      lastTicket: null,
      alertOpen: false,
    }),
}));