import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface UserSummary {
  id: number;
  username: string;
  display_name: string;
  email?: string | null;
  department_id?: number | null;
  is_superuser?: boolean;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserSummary | null;
  roles: string[];
  permissions: string[];
  department: { id: number; name: string; parent_id: number | null } | null;

  setTokens: (access: string, refresh: string) => void;
  setIdentity: (payload: {
    user_info: UserSummary;
    roles: string[];
    permissions: string[];
    department?: { id: number; name: string; parent_id: number | null } | null;
  }) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      roles: [],
      permissions: [],
      department: null,

      setTokens: (access, refreshT) => set({ accessToken: access, refreshToken: refreshT }),
      setIdentity: (payload) =>
        set({
          user: payload.user_info,
          roles: payload.roles,
          permissions: payload.permissions,
          department: payload.department ?? null,
        }),
      clear: () =>
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          roles: [],
          permissions: [],
          department: null,
        }),
    }),
    { name: 'kbms-auth' },
  ),
);