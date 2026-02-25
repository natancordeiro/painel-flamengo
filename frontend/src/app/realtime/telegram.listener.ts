import { useEffect } from "react";
import { useTelegramStore } from "../store/telegram.store";

export function useTelegramRealtime() {
  const { setConnected, setQrCode } = useTelegramStore();

  useEffect(() => {
    const ws = new WebSocket(
      import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws",
    );

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === "telegram.qr") {
        setQrCode(msg.qr);
      }

      if (msg.type === "telegram.connected") {
        setConnected(true);
        setQrCode(null);
      }

      if (msg.type === "telegram.disconnected") {
        setConnected(false);
      }
    };

    return () => ws.close();
  }, []);
}
