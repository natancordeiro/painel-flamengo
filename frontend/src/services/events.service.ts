
import { api } from "./api";
import type { ApiOk } from "../types/api.types";
import type { BackendEvent, GameEvent, GameSector } from "../types/game.types";

function unwrap<T>(payload: ApiOk<T>): T {
  return payload.data;
}

function toGameEvent(e: BackendEvent): GameEvent {
  const name = `${e.home_team} x ${e.away_team}`;
  const dt = new Date(e.event_datetime);
  const datetime_label = Number.isNaN(dt.getTime())
    ? e.event_datetime
    : dt.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });

  return {
    ...e,
    name,
    datetime_label,
  };
}

export const eventsService = {
  async listEvents(accountId: string): Promise<GameEvent[]> {
    const { data } = await api.get<ApiOk<BackendEvent[]>>(
      `/accounts/${accountId}/events`
    );
    return unwrap(data).map(toGameEvent);
  },

  async listSectors(accountId: string, eventId: number): Promise<GameSector[]> {
    const { data } = await api.get<ApiOk<GameSector[]>>(
      `/accounts/${accountId}/events/${eventId}/sectors`
    );
    return unwrap(data);
  },
};