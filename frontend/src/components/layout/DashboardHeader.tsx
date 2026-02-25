
import React from "react";
import { motion } from "framer-motion";
import { FaTelegram, FaServer, FaUsers } from "react-icons/fa";
import { useSystemStore } from "../../app/store/system.store";
import type { SystemStatus } from "../../types/dashboard.types";

interface Props {
  status: SystemStatus;
}

export const DashboardHeader: React.FC<Props> = ({ status }) => {
  const apiOnline = useSystemStore((s) => s.apiOnline);

  return (
    <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between mb-10">
      <div>
        <h1 className="text-white text-4xl font-extrabold tracking-tight">
          Painel de Controle
        </h1>
        <p className="text-white/75 text-sm mt-2">
          Monitoramento em tempo real do sistema
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {/* Sistema */}
        <motion.div
          animate={{ scale: status.system_active ? [1, 1.06, 1] : 1 }}
          transition={{ repeat: Infinity, duration: 2.2 }}
          className={[
            "flex items-center gap-2 px-4 py-2 rounded-2xl font-semibold",
            "shadow-[0_14px_35px_rgba(0,0,0,0.18)]",
            status.system_active ? "bg-emerald-500 text-white" : "bg-red-500 text-white",
          ].join(" ")}
        >
          <FaServer />
          {status.system_active ? "Sistema Online" : "Sistema Offline"}
        </motion.div>

        {/* Telegram */}
        <div
          className={[
            "flex items-center gap-2 px-4 py-2 rounded-2xl font-semibold",
            "shadow-[0_14px_35px_rgba(0,0,0,0.14)]",
            status.telegram_connected ? "bg-emerald-500 text-white" : "bg-white/20 text-white",
            "backdrop-blur-sm",
          ].join(" ")}
        >
          <FaTelegram />
          Telegram
        </div>

        {/* Contas */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-flamengoBlack text-white font-semibold shadow-[0_14px_35px_rgba(0,0,0,0.20)]">
          <FaUsers />
          {status.accounts_count}
        </div>

        {/* API offline */}
        {!apiOnline && (
          <div className="px-4 py-2 rounded-2xl bg-red-700 text-white font-semibold shadow-[0_14px_35px_rgba(0,0,0,0.22)]">
            API Offline
          </div>
        )}
      </div>
    </div>
  );
};
