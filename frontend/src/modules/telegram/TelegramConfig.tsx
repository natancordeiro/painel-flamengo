
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { useTelegramStore } from "../../app/store/telegram.store";
import { telegramService } from "../../services/telegram.service";

export default function TelegramConfig() {
  const {
    connected,
    qrCode,
    connecting,
    setConnecting,
  } = useTelegramStore();

  const connect = async () => {
    try {
      setConnecting(true);
      await telegramService.connect();
      toast.success("Solicitação enviada. Aguarde o QR Code.");
    } catch {
      toast.error("Falha ao iniciar conexão com Telegram.");
      setConnecting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* STATUS */}
      <div className="rounded-3xl bg-white p-6 shadow flex items-center justify-between">
        <div>
          <div className="font-bold text-lg">Telegram Bot</div>
          <div className="text-gray-500 text-sm">
            {connected ? "Conectado" : "Desconectado"}
          </div>
        </div>

        <div
          className={`px-4 py-2 rounded-xl text-white font-semibold ${
            connected ? "bg-green-600" : "bg-red-600"
          }`}
        >
          {connected ? "ONLINE" : "OFFLINE"}
        </div>
      </div>

      {/* QR */}
      {!connected && (
        <div className="rounded-3xl bg-white p-8 shadow text-center">
          <h3 className="font-bold text-xl mb-4">
            Conectar Telegram
          </h3>

          {qrCode ? (
            <img
              src={qrCode}
              alt="QR Telegram"
              className="mx-auto w-64 mb-6"
            />
          ) : (
            <div className="text-gray-400 mb-6">
              Clique para gerar QRCode
            </div>
          )}

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={connect}
            className="btn-premium"
            disabled={connecting}
          >
            {connecting ? "Gerando QR..." : "Conectar Telegram"}
          </motion.button>
        </div>
      )}
    </div>
  );
}