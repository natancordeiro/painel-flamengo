import { useEffect, useRef } from "react";
import { useMonitoringStore } from "../store/monitoring.store";
import { monitoringService } from "../../services/monitoring.service";


export function useMonitoringRealtime() {
  const activeJobId = useMonitoringStore((s) => s.activeJobId);
  const setJob = useMonitoringStore((s) => s.setJob);
  const setLoading = useMonitoringStore((s) => s.setLoading);
  const setError = useMonitoringStore((s) => s.setError);
  const setActive = useMonitoringStore((s) => s.setActive);

  const timerRef = useRef<number | null>(null);

  useEffect(() => {

    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }


    if (!activeJobId) return;

    let cancelled = false;

    const tick = async () => {
      try {
        setLoading(true);
        setError(null);

        const job = await monitoringService.getJob(activeJobId);
        if (cancelled) return;

        setJob(job);
        setActive(job.status === "running");

        // se encerrar para o polling automaticamente
        if (job.status !== "running") {
          if (timerRef.current) {
            window.clearInterval(timerRef.current);
            timerRef.current = null;
          }
        }
      } catch (e) {
        if (cancelled) return;
        const msg = e instanceof Error ? e.message : "Falha ao atualizar monitoramento.";
        setError(msg);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    tick();

    // polling a cada 3s
    timerRef.current = window.setInterval(tick, 3000);

    return () => {
      cancelled = true;
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [activeJobId, setActive, setError, setJob, setLoading]);
}