import { api, extractErrorMessage } from './client';

// ===== Departments =====
export interface DepartmentNode {
  id: number;
  name: string;
  parent_id: number | null;
  leader_id: number | null;
  sort_order: number;
  children: DepartmentNode[];
  created_at: string;
  updated_at: string;
}

export async function listDepartments(): Promise<DepartmentNode[]> {
  const r = await api.get<DepartmentNode[]>('/api/org/departments');
  return r.data;
}

export async function createDepartment(payload: { name: string; parent_id?: number | null; leader_id?: number | null; sort_order?: number }) {
  const r = await api.post('/api/org/departments', payload);
  return r.data;
}

export async function updateDepartment(id: number, payload: Partial<{ name: string; parent_id: number | null; leader_id: number | null; sort_order: number }>) {
  const r = await api.put(`/api/org/departments/${id}`, payload);
  return r.data;
}

export async function deleteDepartment(id: number) {
  await api.delete(`/api/org/departments/${id}`);
}

// ===== Roles =====
export interface Role {
  id: number;
  role_name: string;
  role_code: string;
  description: string | null;
  is_builtin: boolean;
  permissions: string[];
}

export async function listRoles(): Promise<Role[]> {
  const r = await api.get<Role[]>('/api/org/roles');
  return r.data;
}

export async function createRole(payload: { role_name: string; role_code: string; description?: string }) {
  const r = await api.post('/api/org/roles', payload);
  return r.data;
}

export async function replaceRolePermissions(roleId: number, codes: string[]) {
  const r = await api.post(`/api/org/roles/${roleId}/permissions`, { permission_codes: codes });
  return r.data;
}

export interface PermissionEntry {
  id: number;
  permission_code: string;
  resource: string;
  action: string;
}

export async function listPermissions(): Promise<PermissionEntry[]> {
  const r = await api.get<PermissionEntry[]>('/api/org/permissions');
  return r.data;
}

// ===== Users =====
export interface UserDetail {
  id: number;
  username: string;
  display_name: string;
  email: string | null;
  department_id: number | null;
  status: number;
  is_superuser: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
  roles: Role[];
  department: { id: number; name: string } | null;
}

export interface PageResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export async function listUsers(params: {
  page?: number;
  page_size?: number;
  keyword?: string;
  department_id?: number;
  status?: number;
} = {}): Promise<PageResult<UserDetail>> {
  const r = await api.get<PageResult<UserDetail>>('/api/org/users', { params });
  return r.data;
}

export async function createUser(payload: {
  username: string;
  password: string;
  display_name: string;
  email?: string;
  department_id?: number;
  role_ids?: number[];
  status?: number;
}) {
  const r = await api.post('/api/org/users', payload);
  return r.data;
}

export async function updateUser(id: number, payload: Partial<{ display_name: string; email: string; department_id: number | null; role_ids: number[]; status: number }>) {
  const r = await api.put(`/api/org/users/${id}`, payload);
  return r.data;
}

export async function resetPassword(id: number): Promise<{ new_password: string }> {
  const r = await api.post(`/api/org/users/${id}/reset-password`);
  return r.data;
}

export async function toggleUserStatus(id: number) {
  const r = await api.post(`/api/org/users/${id}/toggle-status`);
  return r.data;
}

export async function deleteUser(id: number) {
  await api.delete(`/api/org/users/${id}`);
}

export { extractErrorMessage };