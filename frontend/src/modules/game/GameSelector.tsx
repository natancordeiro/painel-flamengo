
import { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../services/api";
import { useAccountStore } from "../../app/store/account.store";
import { useGameStore } from "../../app/store/game.store";
import type { BackendEvent, GameEvent, GameSector } from "../../types/game.types";

function toPtBrLabel(iso: string): string {
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function toGameEvent(e: BackendEvent): GameEvent {
  return {
    ...e,
    name: `${e.home_team} x ${e.away_team}`,
    datetime_label: e.event_datetime ? toPtBrLabel(e.event_datetime) : "",
  };
}

export default function GameSelector() {
  const activeAccountId = useAccountStore((s) => s.activeAccountId);

  const events = useGameStore((s) => s.events);
  const sectors = useGameStore((s) => s.sectors);
  const activeEvent = useGameStore((s) => s.activeEvent);

  const setEvents = useGameStore((s) => s.setEvents);
  const setSectors = useGameStore((s) => s.setSectors);
  const setActiveEvent = useGameStore((s) => s.setActiveEvent);

  const [loadingEvents, setLoadingEvents] = useState(false);
  const [loadingSectors, setLoadingSectors] = useState(false);

  const title = useMemo(() => "Selecionar Jogo", []);

  useEffect(() => {
    setActiveEvent(null);
    setSectors([]);
    setEvents([]);
  }, [activeAccountId, setActiveEvent, setEvents, setSectors]);

  useEffect(() => {
    if (!activeAccountId) return;

    const loadEvents = async () => {
      try {
        setLoadingEvents(true);

        const { data } = await api.get(`/accounts/${activeAccountId}/events`);
        const raw = (data?.data ?? []) as BackendEvent[];
        const mapped = raw.map(toGameEvent);

        setEvents(mapped);
      } catch {
        toast.error("Falha ao carregar jogos.");
        setEvents([]);
      } finally {
        setLoadingEvents(false);
      }
    };

    loadEvents();
  }, [activeAccountId, setEvents]);

  const selectEvent = async (event: GameEvent) => {
    if (!activeAccountId) return;

    try {
      setLoadingSectors(true);
      setActiveEvent(event);
      setSectors([]);

      const { data } = await api.get(
        `/accounts/${activeAccountId}/events/${event.id}/sectors`
      );

      const raw = (data?.data ?? []) as GameSector[];
      setSectors(raw);

      toast.success("Jogo selecionado.");
    } catch {
      toast.error("Falha ao carregar setores.");
      setSectors([]);
    } finally {
      setLoadingSectors(false);
    }
  };

  if (!activeAccountId) {
    return (
      <div className="text-gray-500">
        Selecione uma conta logada para buscar jogos.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">{title}</h2>

      {loadingEvents && (
        <div className="text-gray-500">Carregando jogos...</div>
      )}

      {!loadingEvents && events.length === 0 && (
        <div className="text-gray-500">Nenhum jogo encontrado.</div>
      )}

      {events.map((event) => {
        const isActive = activeEvent?.id === event.id;

        return (
          <div
            key={event.id}
            className={`p-4 rounded-xl border cursor-pointer ${
              isActive
                ? "border-emerald-500 bg-emerald-50"
                : "border-gray-200 bg-white"
            }`}
            onClick={() => selectEvent(event)}
          >
            <div className="font-bold">{event.name}</div>
            <div className="text-sm text-gray-600">{event.championship}</div>
            {event.datetime_label && (
              <div className="text-sm text-gray-600">{event.datetime_label}</div>
            )}
            {event.stadium && (
              <div className="text-xs text-gray-500">{event.stadium}</div>
            )}
          </div>
        );
      })}

      {activeEvent && (
        <div className="mt-6">
          <h3 className="font-bold mb-3">Setores</h3>

          {loadingSectors && (
            <div className="text-gray-500">Carregando setores...</div>
          )}

          {!loadingSectors && sectors.length === 0 && (
            <div className="text-gray-500">Nenhum setor disponível.</div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {sectors.map((s) => (
              <div
                key={s.id}
                className="p-3 rounded-xl border bg-white text-sm"
              >
                {s.name}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}