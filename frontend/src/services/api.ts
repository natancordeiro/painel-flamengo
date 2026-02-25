
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      console.error(
        "[API ERROR]",
        status,
        data?.error?.message || data || error.message
      );
    } else {
      console.error("[API ERROR]", error.message);
    }

    return Promise.reject(error);
  }
);