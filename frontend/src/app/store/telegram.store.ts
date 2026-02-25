import { create } from "zustand";

interface TelegramState {
  connected: boolean;
  qrCode: string | null;
  connecting: boolean;

  setConnected: (v: boolean) => void;
  setQrCode: (qr: string | null) => void;
  setConnecting: (v: boolean) => void;
}

export const useTelegramStore = create<TelegramState>((set) => ({
  connected: false,
  qrCode: null,
  connecting: false,

  setConnected: (v) => set({ connected: v }),
  setQrCode: (qr) => set({ qrCode: qr }),
  setConnecting: (v) => set({ connecting: v }),
}));
