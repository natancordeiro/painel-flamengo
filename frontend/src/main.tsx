import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import RealtimeProvider from "./app/realtime/RealtimeProvider";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RealtimeProvider>
      <App />
    </RealtimeProvider>
  </StrictMode>
);
