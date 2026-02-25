
export interface BackendEvent {
  id: number;
  championship: string;
  home_team: string;
  away_team: string;
  event_datetime: string;
  stadium?: string | null;
  url: string;
}

export interface GameSector {
  id: number;
  name: string;
}

export type GameEvent = BackendEvent & {
  name: string;
  datetime_label: string;
};