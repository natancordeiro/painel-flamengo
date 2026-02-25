
import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaTicketAlt } from "react-icons/fa";
import { useMonitoringStore } from "../../app/store/monitoring.store";
import type { TicketRealtime } from "../../app/store/monitoring.store";

export default function TicketAlertGlobal() {
  const alertOpen = useMonitoringStore((s) => s.alertOpen);
  const lastTicket = useMonitoringStore((s) => s.lastTicket);
  const closeAlert = useMonitoringStore((s) => s.closeAlert);

  useEffect(() => {
    if (!alertOpen) return;

    const t = setTimeout(() => {
      closeAlert();
    }, 4200);

    return () => clearTimeout(t);
  }, [alertOpen, closeAlert]);

  const ticket: TicketRealtime | null = lastTicket;

  return (
    <AnimatePresence>
      {alertOpen && ticket && (
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 40, scale: 0.96 }}
          transition={{ duration: 0.22, ease: "easeOut" }}
          className="
            fixed bottom-6 right-6 z-[9999]
            w-[360px]
          "
        >
          <div
            className="
              relative overflow-hidden
              rounded-3xl
              p-5
              text-white
              shadow-[0_30px_120px_rgba(0,0,0,0.6)]
              bg-gradient-to-br
              from-[#111111]
              via-[#1a1a1a]
              to-[#C8102E]
              border border-white/10
              backdrop-blur-lg
            "
          >
            {/* brilho */}
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-red-600/40 blur-[80px]" />

            <div className="relative flex items-start gap-4">
              <FaTicketAlt className="text-3xl text-red-400 mt-1" />

              <div className="flex-1">
                <div className="font-extrabold text-lg tracking-tight">
                  INGRESSO ENCONTRADO
                </div>

                <div className="text-sm opacity-90 mt-1">{ticket.match}</div>

                <div className="text-sm mt-2">
                  Setor: <span className="font-semibold">{ticket.setor}</span>
                </div>

                <div className="text-sm">
                  Quantidade:{" "}
                  <span className="font-semibold">{ticket.quantity}</span>
                </div>

                <div className="text-xs text-white/70 mt-2">{ticket.datetime}</div>

                <button
                  type="button"
                  onClick={closeAlert}
                  className="mt-4 w-full py-2 rounded-xl bg-white/15 hover:bg-white/25 transition font-semibold"
                >
                  OK
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
