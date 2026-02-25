
import { motion } from "framer-motion";
import { DashboardCard } from "../components/dashboard/DashboardCard";
import { ActionCard } from "../components/dashboard/ActionCard";
import { DashboardHeader } from "../components/layout/DashboardHeader";
import { DashboardWorkspace } from "../components/dashboard/DashboardWorkspace";
import { SkeletonCard } from "../components/ui/SkeletonCard";
import {
  FaTelegram,
  FaRobot,
  FaFutbol,
  FaUser,
  FaSearch,
  FaCog,
} from "react-icons/fa";
import { useCallback, useEffect, useMemo, useState } from "react";
import { getSystemStatus } from "../services/dashboard.service";
import { useSystemStore } from "../app/store/system.store";

import AccountSettings from "../modules/account/AccountSettings";
import TelegramConfig from "../modules/telegram/TelegramConfig";
import GameSelector from "../modules/game/GameSelector";
import MonitoringPanel from "../modules/monitoring/MonitoringPanel";

type Section =
  | "accounts"
  | "telegram"
  | "game"
  | "system"
  | "manage"
  | "configTelegram"
  | "selectGame"
  | "monitoring"
  | null;

const containerVariants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.06, delayChildren: 0.05 },
  },
};

export default function DashboardPage() {
  const [section, setSection] = useState<Section>(null);
  const [loading, setLoading] = useState(true);

  // seletores
  const status = useSystemStore((s) => s.status);
  const setStatus = useSystemStore((s) => s.setStatus);
  const setApiOnline = useSystemStore((s) => s.setApiOnline);

  /* acesso liberado */
  const guard = useCallback((target: Section) => {
    setSection(target);
  }, []);

  const closeWorkspace = useCallback(() => setSection(null), []);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const data = await getSystemStatus();
        if (!mounted) return;
        setStatus(data);
        setApiOnline(true);
        setLoading(false);
      } catch (err) {
        console.error("Erro ao carregar status:", err);
        if (!mounted) return;
        setApiOnline(false);
      }
    };

    load();
    const interval = setInterval(load, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [setApiOnline, setStatus]);

  useEffect(() => {
    const close = () => setSection(null);
    document.addEventListener("closeWorkspace", close);
    return () => document.removeEventListener("closeWorkspace", close);
  }, []);

  const workspaceTitle = useMemo(() => {
    return section === "accounts"
      ? "Conta"
      : section === "configTelegram"
      ? "Configurar Telegram"
      : section === "selectGame"
      ? "Selecionar jogo"
      : "Monitoramento";
  }, [section]);

  if (loading) {
    return (
      <div className="min-h-screen w-full bg-gradient-to-br from-[#ff1e3c] via-[#C8102E] to-[#7a0c1c] relative overflow-hidden p-8">
        {/* vermelho superior */}
        <div className="pointer-events-none fixed -top-40 -left-40 w-[650px] h-[650px] bg-red-500/50 blur-[120px]" />
        {/* vermelho central */}
        <div className="pointer-events-none fixed top-[35%] left-[35%] w-[550px] h-[550px] bg-[#ff304f]/45 blur-[140px]" />
        {/* profundidade inferior */}
        <div className="pointer-events-none fixed bottom-0 right-0 w-[700px] h-[700px] bg-black/20 blur-[200px]" />

        <div className="relative grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen overflow-hidden p-8 text-white">
      {/* BASE GRADIENT */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-[#0f0f0f] via-[#1a1a1a] to-[#C8102E]" />

      {/* vermelho superior */}
      <div className="absolute -top-40 -left-40 w-[650px] h-[650px] bg-red-600/35 blur-[120px]" />
      {/* vermelho central */}
      <div className="absolute top-[30%] left-[35%] w-[550px] h-[550px] bg-[#ff2a4d]/30 blur-[140px]" />
      {/* profundidade inferior */}
      <div className="absolute bottom-0 right-0 w-[700px] h-[700px] bg-black/40 blur-[200px]" />

      <div className="relative max-w-6xl mx-auto">
        <DashboardHeader status={status} />

        {/* KPI CARDS */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
        >
          <DashboardCard
            variant="kpi"
            title="Contas"
            icon={<FaUser className="text-indigo-600" />}
            status="Disponível"
            active={true}
            onClick={() => setSection("accounts")}
          />

          <DashboardCard
            variant="kpi"
            title="Telegram"
            icon={<FaTelegram className="text-sky-500" />}
            status={status.telegram_connected ? "Configurado" : "Desconectado"}
            active={status.telegram_connected}
            onClick={() => guard("configTelegram")}
          />

          <DashboardCard
            variant="kpi"
            title="Jogo Ativo"
            icon={<FaFutbol className="text-emerald-600" />}
            status={status.active_game ? "Ativo" : "Inativo"}
            active={status.active_game}
            onClick={() => guard("selectGame")}
          />

          <DashboardCard
            variant="kpi"
            title="Sistema"
            icon={<FaRobot className="text-violet-600" />}
            status={status.system_active ? "Ativo" : "Offline"}
            active={status.system_active}
            onClick={() => guard("monitoring")}
          />
        </motion.div>

        {/* ação dos cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          <ActionCard
            title="Gerenciar Conta"
            description="Perfil, segurança e preferências do sistema."
            icon={<FaCog className="text-flamengoBlack" />}
            ctaLabel="Abrir"
            onClick={() => setSection("accounts")}
          />

          <ActionCard
            title="Configurar Telegram"
            description="Conectar bot, validar credenciais e testar notificações."
            icon={<FaTelegram className="text-sky-500" />}
            ctaLabel="Configurar"
            onClick={() => guard("configTelegram")}
          />

          <ActionCard
            title="Selecionar Jogo"
            description="Buscar partidas disponíveis e iniciar monitoramento."
            icon={<FaSearch className="text-emerald-600" />}
            ctaLabel="Buscar"
            onClick={() => guard("selectGame")}
          />

          <ActionCard
            title="Monitoramento"
            description="Status do sistema e eventos em tempo real."
            icon={<FaRobot className="text-violet-600" />}
            ctaLabel="Ver status"
            onClick={() => guard("monitoring")}
          />
        </motion.div>

        <DashboardWorkspace
          isOpen={section !== null}
          onClose={closeWorkspace}
          title={workspaceTitle}
        >
          {section === "accounts" && <AccountSettings />}
          {section === "configTelegram" && <TelegramConfig />}
          {section === "selectGame" && <GameSelector />}
          {section === "monitoring" && <MonitoringPanel />}
        </DashboardWorkspace>
      </div>
    </div>
  );
}
