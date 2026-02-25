
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../services/api";
import { useAccountStore } from "../../app/store/account.store";
import type { Account } from "../../app/store/account.store";

export default function AccountSettings() {
  const { accounts, activeAccountId, setAccounts, setActiveAccount } =
    useAccountStore();

  const [loading, setLoading] = useState(false);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const { data } = await api.get("/accounts");
      setAccounts(data.data);
    } catch {
      toast.error("Falha ao carregar contas.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  const login = async (account: Account) => {
    try {
      await api.post(`/accounts/${account.id}/login`);
      toast.success("Conta logada com sucesso.");
      await loadAccounts();
      setActiveAccount(account.id);
    } catch {
      toast.error("Falha ao efetuar login.");
    }
  };

  const logout = async (account: Account) => {
    try {
      await api.post(`/accounts/${account.id}/logout`);
      toast.success("Conta desconectada.");
      await loadAccounts();
      if (activeAccountId === account.id) setActiveAccount(null);
    } catch {
      toast.error("Falha ao efetuar logout.");
    }
  };

  const selectActive = (accountId: string) => {
    setActiveAccount(accountId);
    toast.success("Conta ativa selecionada.");
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Contas do Flamengo</h2>

      {loading && <div className="text-gray-500">Carregando...</div>}

      {!loading && accounts.length === 0 && (
        <div className="text-gray-500">Nenhuma conta cadastrada.</div>
      )}

      {accounts.map((acc) => {
        const isActive = activeAccountId === acc.id;

        return (
          <div
            key={acc.id}
            className={`bg-white rounded-2xl shadow p-6 flex items-center justify-between border ${
              isActive ? "border-emerald-500" : "border-transparent"
            }`}
          >
            <div>
              <div className="font-bold flex items-center gap-2">
                {acc.label}
                {isActive && (
                  <span className="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700">
                    ATIVA
                  </span>
                )}
              </div>

              <div className="text-sm text-gray-600">{acc.email}</div>

              <div className="text-sm">
                Status:{" "}
                <span
                  className={
                    acc.logged ? "text-green-600" : "text-red-600"
                  }
                >
                  {acc.logged ? "Logada" : "Desconectada"}
                </span>
              </div>

              {acc.logged && acc.logged_user && (
                <div className="text-xs text-gray-500 mt-1">
                  Usuário:{" "}
                  <span className="font-semibold">{acc.logged_user}</span>
                </div>
              )}
            </div>

            <div className="flex gap-3">
              {acc.logged && !isActive && (
                <button
                  onClick={() => selectActive(acc.id)}
                  className="btn-premium"
                >
                  Usar esta
                </button>
              )}

              {!acc.logged && (
                <button
                  onClick={() => login(acc)}
                  className="btn-premium"
                >
                  Login
                </button>
              )}

              {acc.logged && (
                <button
                  onClick={() => logout(acc)}
                  className="btn-premium bg-red-600"
                >
                  Logout
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}