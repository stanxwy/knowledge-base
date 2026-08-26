import { api } from './client';

export interface UnitPermission {
  id?: number;
  target_type: 'global' | 'department' | 'role' | 'user';
  target_id: number | null;
}

export interface KnowledgeUnit {
  id: number;
  unit_code: string;
  title: string;
  content: string;
  summary: string | null;
  category: string | null;
  tags: string[] | null;
  status: 'draft' | 'published' | 'archived';
  creator_id: number;
  source_file_name: string | null;
  file_type: string | null;
  file_size: number | null;
  created_at: string;
  updated_at: string;
  permissions?: UnitPermission[];
}

export interface PageResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export async function listUnits(params: {
  page?: number;
  page_size?: number;
  keyword?: string;
  category?: string;
  status?: string;
} = {}): Promise<PageResult<KnowledgeUnit>> {
  const r = await api.get<PageResult<KnowledgeUnit>>('/api/knowledge/units', { params });
  return r.data;
}

export async function getUnit(id: number): Promise<KnowledgeUnit> {
  const r = await api.get<KnowledgeUnit>(`/api/knowledge/units/${id}`);
  return r.data;
}

export async function createUnit(payload: Partial<KnowledgeUnit>) {
  const r = await api.post('/api/knowledge/units', payload);
  return r.data as KnowledgeUnit;
}

export async function updateUnit(id: number, payload: Partial<KnowledgeUnit>) {
  const r = await api.put(`/api/knowledge/units/${id}`, payload);
  return r.data;
}

export async function batchDeleteUnits(unit_ids: number[]) {
  const r = await api.delete('/api/knowledge/units', { data: { unit_ids } });
  return r.data as { deleted: number };
}

export async function replaceUnitPermissions(id: number, permissions: UnitPermission[]) {
  const r = await api.post(`/api/knowledge/units/${id}/permissions`, { permissions });
  return r.data;
}

export async function checkPermissions(user_id: number, unit_ids: number[]) {
  const r = await api.post('/api/knowledge/check-permissions', { user_id, unit_ids });
  return r.data as { authorized_unit_ids: number[]; unauthorized_unit_ids: number[] };
}

export interface ImportTaskFileResult {
  filename: string;
  status: 'pending' | 'parsing' | 'ingesting' | 'uploaded' | 'processing' | 'done' | 'failed' | 'timeout';
  unit_codes: string[];
  unit_ids: number[];
  error: string | null;
  message: string | null;
  done_list: string[];
  running_list: string[];
}

export interface ImportTaskStatus {
  task_id: string;
  status: 'pending' | 'running' | 'done' | 'failed' | 'timeout';
  files: ImportTaskFileResult[];
  created_at: string;
  updated_at: string;
}

export async function importFiles(files: File[]): Promise<ImportTaskStatus> {
export async function importFiles(files: File[]): Promise<ImportTaskStatus> {
  const form = new FormData();
  for (const f of files) form.append('files', f);
  const r = await api.post<ImportTaskStatus>('/api/knowledge/import', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  });
  return r.data;
}

export async function pollImportTask(taskId: string): Promise<ImportTaskStatus> {
  const r = await api.get<ImportTaskStatus>(`/api/knowledge/tasks/${taskId}`);
  return r.data;
}

export async function pollAppTaskProgress(taskId: string): Promise<{
  task_id: string;
  status: string;
  done_list: string[];
  running_list: string[];
}> {
  // Reuse app's /status/{task_id} endpoint for real-time progress
  const r = await api.get<{
    task_id: string;
    status: string;
    done_list: string[];
    running_list: string[];
  }>(`/api/v1/status/${taskId}`);
  return r.data;
}
