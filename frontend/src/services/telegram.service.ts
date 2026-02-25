
import { api } from "./api";

export const telegramService = {
  async connect() {
    await api.post("/telegram/connect");
  },

  async disconnect() {
    await api.post("/telegram/disconnect");
  },
};