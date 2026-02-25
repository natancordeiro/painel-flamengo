import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaTimes } from "react-icons/fa";

interface Props {
  title: string;
  isOpen: boolean;
  onClose?: () => void;
  children: React.ReactNode;
}

export const DashboardWorkspace: React.FC<Props> = ({
  title,
  isOpen,
  onClose,
  children,
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* BACKDROP */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="fixed inset-0 z-40"
          >
            <div className="absolute inset-0 bg-black/60 backdrop-blur-[6px]" />

            {/* vermelho */}
            <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-red-600/30 blur-[180px]" />
            <div className="absolute -bottom-40 -right-40 w-[600px] h-[600px] bg-black blur-[180px]" />
          </motion.div>

          {/* MODAL */}
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: 40 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.92, y: 40 }}
            transition={{ duration: 0.22, ease: "easeOut" }}
            className="fixed z-50 inset-0 flex items-center justify-center p-6"
          >
            <div
              className="
                relative w-full max-w-2xl
                rounded-3xl
                bg-gradient-to-br
                from-[#111111]
                via-[#1a1a1a]
                to-[#C8102E]
                text-white
                border border-white/10
                shadow-[0_40px_160px_rgba(0,0,0,0.65)]
                p-8
                overflow-hidden
              "
            >
              {/* brilho interno */}
              <div className="absolute -top-24 -right-24 w-72 h-72 bg-red-500/25 blur-[120px]" />
              <div className="absolute -bottom-24 -left-24 w-72 h-72 bg-black blur-[120px]" />

              {/* CLOSE */}
              <button
                onClick={onClose}
                className="
                  absolute top-5 right-5
                  w-9 h-9 rounded-full
                  bg-white/10 hover:bg-white/20
                  flex items-center justify-center
                  transition
                "
              >
                <FaTimes className="text-white" />
              </button>

              {/* HEADER */}
              <h2 className="text-2xl font-extrabold tracking-tight mb-6">
                {title}
              </h2>

              {/* CONTENT */}
              <div className="relative max-h-[65vh] overflow-auto pr-2">
                {children}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
