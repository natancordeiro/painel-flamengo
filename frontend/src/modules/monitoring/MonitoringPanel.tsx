
import { useEffect, useMemo, useRef, useState } from "react";
import { FaFutbol, FaTicketAlt } from "react-icons/fa";
import toast from "react-hot-toast";

import { useMonitoringStore } from "../../app/store/monitoring.store";
import { useAccountStore } from "../../app/store/account.store";
import { monitoringService } from "../../services/monitoring.service";

const POLL_INTERVAL_MS = 5000;

export default function MonitoringPanel() {
  const activeAccountId = useAccountStore((s) => s.activeAccountId);

  const active = useMonitoringStore((s) => s.active);
  const tickets = useMonitoringStore((s) => s.tickets);
  const loading = useMonitoringStore((s) => s.loading);
  const lastError = useMonitoringStore((s) => s.lastError);
  const activeJobId = useMonitoringStore((s) => s.activeJobId);

  const setActive = useMonitoringStore((s) => s.setActive);
  const setActiveJobId = useMonitoringStore((s) => s.setActiveJobId);
  const setJob = useMonitoringStore((s) => s.setJob);
  const setError = useMonitoringStore((s) => s.setError);
  const setLoading = useMonitoringStore((s) => s.setLoading);

  const [eventId, setEventId] = useState<string>("");

  const pollRef = useRef<number | null>(null);

  const buttonLabel = useMemo(() => {
    if (loading) return "Processando...";
    return active ? "Parar" : "Continuar";
  }, [active, loading]);

  useEffect(() => {
    if (!active || !activeJobId) return;

    const poll = async () => {
      try {
        const job = await monitoringService.getJob(activeJobId);
        setJob(job);

        if (job.status !== "running") {
          setActive(false);
          setActiveJobId(null);
          toast(`Monitoramento finalizado (${job.status}).`);
          stopPolling();
        }
      } catch (e) {
        const msg =
          e instanceof Error
            ? e.message
            : "Erro ao consultar status do monitoramento.";
        setError(msg);
        toast.error(msg);
      }
    };

    const startPolling = () => {
      poll();
      pollRef.current = window.setInterval(poll, POLL_INTERVAL_MS);
    };

    const stopPolling = () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };

    startPolling();

    return () => stopPolling();
  }, [active, activeJobId, setActive, setActiveJobId, setJob, setError]);

  // ▶ START / ⏹ STOP
  const toggle = async () => {
    try {
      setError(null);

      if (!activeAccountId) {
        toast.error("Selecione uma conta antes de iniciar o monitoramento.");
        return;
      }

      // ▶INICIAR
      if (!active) {
        const idNum = Number(eventId);
        if (!Number.isFinite(idNum) || idNum <= 0) {
          toast.error("Informe um Event ID válido (ex.: 12345).");
          return;
        }

        setLoading(true);

        const res = await monitoringService.startJob({
          account_id: activeAccountId,
          event_id: idNum,
        });

        setActiveJobId(res.job_id);
        setActive(true);

        toast.success("Monitoramento iniciado.");
        return;
      }

      // ⏹PARAR
      if (!activeJobId) {
        setActive(false);
        toast("Nenhum job ativo para parar.");
        return;
      }

      setLoading(true);

      await monitoringService.stopJob(activeJobId);

      const job = await monitoringService.getJob(activeJobId);
      setJob(job);

      setActive(false);
      setActiveJobId(null);

      toast.success("Monitoramento parado.");
    } catch (e) {
      const msg =
        e instanceof Error
          ? e.message
          : "Falha ao controlar o monitoramento.";
      toast.error(msg);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* CONTROLE */}
      <div className="bg-white rounded-3xl p-6 shadow flex items-center justify-between">
        <div className="flex items-center gap-4">
          <FaFutbol className="text-3xl text-red-600" />
          <div>
            <div className="font-bold text-lg">Controle de Monitoramento</div>
            <div className="text-gray-500 text-sm">
              Monitoramento em background (polling)
            </div>
          </div>
        </div>

        <button
          onClick={toggle}
          disabled={loading}
          className={`px-6 py-2 rounded-xl text-white ${
            active ? "bg-red-600" : "bg-green-600"
          } ${loading ? "opacity-70 cursor-not-allowed" : ""}`}
        >
          {buttonLabel}
        </button>
      </div>

      {/* CONFIGURAÇÃO */}
      <div className="bg-white rounded-3xl p-6 shadow space-y-3">
        <div className="font-bold text-lg">Configuração</div>

        <div className="text-sm text-gray-600">
          Conta ativa:{" "}
          <span className="font-semibold">
            {activeAccountId ?? "nenhuma"}
          </span>
        </div>

        <input
          className="border p-3 rounded-xl w-full"
          placeholder="Event ID (ex.: 12345)"
          value={eventId}
          onChange={(e) => setEventId(e.target.value)}
          disabled={active}
        />

        {lastError && (
          <div className="text-sm text-red-600">{lastError}</div>
        )}

        {activeJobId && (
          <div className="text-sm text-gray-700">
            Job ativo:{" "}
            <span className="font-semibold">{activeJobId}</span>
          </div>
        )}
      </div>

      {/* CARRINHO MONITORADO */}
      <div className="bg-white rounded-3xl p-8 shadow">
        <h3 className="text-xl font-bold mb-6">Carrinho Monitorado</h3>

        {tickets.length === 0 && (
          <div className="text-gray-500">
            Nenhum ingresso encontrado ainda...
          </div>
        )}

        {tickets.map((t) => (
          <div
            key={t.id}
            className="border rounded-2xl p-6 flex items-start gap-4 mb-4"
          >
            <FaTicketAlt className="text-2xl text-red-600" />
            <div>
              <div className="font-bold">{t.match}</div>
              <div>Setor: {t.setor}</div>
              <div>Competição: {t.competition}</div>
              <div>Local: {t.location || "—"}</div>
              <div className="font-bold mt-2">{t.price || "—"}</div>
              <div className="text-sm text-gray-600">{t.type}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}