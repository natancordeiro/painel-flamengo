import type { ReactNode } from "react";
import { useMonitoringRealtime } from "./monitoring.listener";
import { useTelegramRealtime } from "./telegram.listener";

export default function RealtimeProvider({
  children,
}: {
  children: ReactNode;
}) {
  useMonitoringRealtime();
  useTelegramRealtime();

  return <>{children}</>;
}
