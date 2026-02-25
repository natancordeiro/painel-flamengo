import React from "react";
import { motion } from "framer-motion";

type Variant = "kpi" | "action";

interface Props {
  title: string;
  icon: React.ReactNode;
  status?: string;
  active?: boolean;
  variant?: Variant;
  onClick?: () => void;
}

export const DashboardCard: React.FC<Props> = ({
  title,
  icon,
  status,
  active = true,
  variant = "kpi",
  onClick,
}) => {
  const isKpi = variant === "kpi";

  const aura = active
    ? "shadow-[0_18px_45px_rgba(16,185,129,0.18)]"
    : "shadow-[0_18px_45px_rgba(239,68,68,0.14)]";

  const ring = active
    ? "ring-1 ring-emerald-500/20"
    : "ring-1 ring-red-500/20";

  return (
    <motion.button
      type="button"
      onClick={onClick}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      style={{ willChange: "transform" }}
      className={[
        "relative w-full text-left rounded-3xl bg-white/95 backdrop-blur-sm",
        "border border-black/5",
        "transform-gpu transition-transform duration-150 ease-out",
        "cursor-pointer select-none overflow-hidden",
        ring,
        aura,
        isKpi ? "p-6" : "p-8",
      ].join(" ")}
    >
      <span className="pointer-events-none absolute inset-0">
        <span
          className={[
            "absolute -top-24 -right-24 h-56 w-56 rounded-full blur-3xl opacity-60",
            active ? "bg-emerald-400/25" : "bg-red-400/20",
          ].join(" ")}
        />
        <span className="absolute inset-0 bg-gradient-to-b from-white/40 to-transparent" />
      </span>

      <div className="relative flex flex-col items-center justify-center text-center">
        <div className={isKpi ? "text-[34px] mb-3" : "text-4xl mb-3"}>
          {icon}
        </div>

        <h3 className="text-[16px] font-extrabold tracking-tight text-flamengoBlack">
          {title}
        </h3>

        {status && (
          <div className="mt-2 flex items-center gap-2">
            <span
              className={[
                "h-2.5 w-2.5 rounded-full",
                active ? "bg-emerald-500" : "bg-red-500",
              ].join(" ")}
            />
            <span
              className={[
                "font-semibold text-sm",
                active ? "text-emerald-700" : "text-red-600",
              ].join(" ")}
            >
              {status}
            </span>
          </div>
        )}
      </div>
    </motion.button>
  );
};
