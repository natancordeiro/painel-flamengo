
import { create } from "zustand";
import type { GameEvent, GameSector } from "../../types/game.types";

interface GameState {

  events: GameEvent[];
  sectors: GameSector[];
  activeEvent: GameEvent | null;


  loadingEvents: boolean;
  loadingSectors: boolean;

  setEvents: (events: GameEvent[]) => void;
  setSectors: (sectors: GameSector[]) => void;
  setActiveEvent: (event: GameEvent | null) => void;

  setLoadingEvents: (v: boolean) => void;
  setLoadingSectors: (v: boolean) => void;

  clear: () => void;
}

export const useGameStore = create<GameState>((set) => ({
  events: [],
  sectors: [],
  activeEvent: null,

  loadingEvents: false,
  loadingSectors: false,

  setEvents: (events) => set({ events }),
  setSectors: (sectors) => set({ sectors }),
  setActiveEvent: (event) =>
    set({
      activeEvent: event,
      sectors: event ? [] : [],
    }),

  setLoadingEvents: (v) => set({ loadingEvents: v }),
  setLoadingSectors: (v) => set({ loadingSectors: v }),

  clear: () =>
    set({
      events: [],
      sectors: [],
      activeEvent: null,
      loadingEvents: false,
      loadingSectors: false,
    }),
}));