import React from "react";
import { motion } from "framer-motion";

interface ActionCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  ctaLabel?: string;
  onClick?: () => void;
}

export const ActionCard: React.FC<ActionCardProps> = ({
  title,
  description,
  icon,
  ctaLabel = "Abrir",
  onClick,
}) => {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.985 }}
      style={{ willChange: "transform" }}
      className={[
        "relative w-full text-left rounded-3xl bg-white",
        "border border-black/5",
        "transform-gpu transition-transform duration-150 ease-out",
        "shadow-[0_18px_55px_rgba(0,0,0,0.14)]",
        "p-10 cursor-pointer overflow-hidden",
      ].join(" ")}
    >
      <span className="pointer-events-none absolute inset-0">
        <span className="absolute -top-24 -left-24 h-60 w-60 rounded-full bg-black/5 blur-3xl" />
        <span className="absolute inset-0 bg-gradient-to-b from-white to-white/70" />
      </span>

      <div className="relative flex flex-col items-center justify-center text-center">
        <div className="text-5xl mb-4">{icon}</div>

        <h3 className="text-xl font-extrabold tracking-tight text-flamengoBlack mb-2">
          {title}
        </h3>

        <p className="text-gray-600 text-center max-w-[22rem] mb-6">
          {description}
        </p>

        <span className="btn-premium">
          {ctaLabel}
          <motion.span
            aria-hidden
            initial={{ x: 0 }}
            whileHover={{ x: 3 }}
            transition={{ duration: 0.15 }}
          >
            →
          </motion.span>
        </span>
      </div>
    </motion.button>
  );
};
