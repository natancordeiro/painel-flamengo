import { create } from "zustand";
import type { SystemStatus } from "../../types/dashboard.types";

type StatusUpdater = SystemStatus | ((prev: SystemStatus) => SystemStatus);

interface SystemState {
  status: SystemStatus;
  apiOnline: boolean;

  setStatus: (updater: StatusUpdater) => void;
  setApiOnline: (value: boolean) => void;
}

export const useSystemStore = create<SystemState>((set, get) => ({
  status: {
    system_active: false,
    telegram_connected: false,
    active_game: false,
    accounts_count: 0,
  },
  apiOnline: true,

  setStatus: (updater) => {
    const prev = get().status;
    const next = typeof updater === "function" ? updater(prev) : updater;
    set({ status: next });
  },

  setApiOnline: (value) => set({ apiOnline: value }),
}));