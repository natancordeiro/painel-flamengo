
import { create } from "zustand";

export interface Account {
  id: string;
  label: string;
  email: string;
  logged: boolean;
  logged_user?: string | null;
  logged_in_at?: string | null;
}

interface AccountState {
  accounts: Account[];
  activeAccountId: string | null;
  loading: boolean;

  setAccounts: (accounts: Account[]) => void;
  setActiveAccount: (accountId: string | null) => void;
  updateAccount: (account: Account) => void;
}

export const useAccountStore = create<AccountState>((set) => ({
  accounts: [],
  activeAccountId: null,
  loading: false,

  setAccounts: (accounts) => set({ accounts }),

  setActiveAccount: (accountId) =>
    set({ activeAccountId: accountId }),

  updateAccount: (account) =>
    set((state) => ({
      accounts: state.accounts.map((a) =>
        a.id === account.id ? account : a
      ),
    })),
}));