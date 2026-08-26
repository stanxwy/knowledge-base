import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../store/auth';

export const api: AxiosInstance = axios.create({
  baseURL: '/',
  timeout: 30000,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`);
  }
  return config;
});

let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshing) return refreshing;
  refreshing = (async () => {
    const { refreshToken, setTokens, clear } = useAuthStore.getState();
    if (!refreshToken) {
      clear();
      return null;
    }
    try {
      const r = await axios.post('/api/auth/refresh', { refresh_token: refreshToken });
      setTokens(r.data.access_token, r.data.refresh_token);
      return r.data.access_token as string;
    } catch (e) {
      clear();
      return null;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

api.interceptors.response.use(
  (resp) => resp,
  async (err: AxiosError) => {
    const status = err.response?.status;
    const originalConfig = err.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (status === 401 && originalConfig && !originalConfig._retry) {
      originalConfig._retry = true;
      const newToken = await refreshAccessToken();
      if (newToken) {
        originalConfig.headers.set('Authorization', `Bearer ${newToken}`);
        return api(originalConfig);
      }
      // refresh failed → force re-login
      window.location.href = '/admin/login';
    }
    return Promise.reject(err);
  },
);

export interface ApiError {
  error: { code: string; message: string; detail?: unknown };
}

export function extractErrorMessage(e: unknown): string {
  const data = (e as AxiosError<ApiError>)?.response?.data;
  return data?.error?.message ?? (e as Error)?.message ?? '请求失败';
}