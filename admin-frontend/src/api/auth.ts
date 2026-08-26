import { api } from './client';
import type { UserSummary } from '../store/auth';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user_info: UserSummary;
  permissions: string[];
}

export interface CurrentUserResponse {
  user_info: UserSummary;
  roles: string[];
  permissions: string[];
  department: { id: number; name: string; parent_id: number | null } | null;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const r = await api.post<LoginResponse>('/api/auth/login', { username, password });
  return r.data;
}

export async function fetchMe(): Promise<CurrentUserResponse> {
  const r = await api.get<CurrentUserResponse>('/api/auth/me');
  return r.data;
}

export async function logout(): Promise<void> {
  await api.post('/api/auth/logout');
}