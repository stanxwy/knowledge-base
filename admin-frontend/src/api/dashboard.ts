import { api } from './client';

export interface DashboardMetrics {
  total_visits: number;
  unique_visitors: number;
  total_knowledge_units: number;
  total_tokens: number;
  avg_response_time_ms: number;
  range: string;
}

export interface QuestionRank {
  question_pattern: string;
  ask_count: number;
  last_asked_at: string | null;
}

export interface UnitRank {
  unit_id: number;
  unit_code: string | null;
  title: string;
  mention_count: number;
}

export interface DailyTrendPoint {
  date: string;
  visits: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  avg_response_time_ms: number;
}

export async function getMetrics(range = '7d'): Promise<DashboardMetrics> {
  const r = await api.get<DashboardMetrics>('/api/dashboard/metrics', { params: { range } });
  return r.data;
}

export async function getQuestionRankings(range = '7d', limit = 10): Promise<QuestionRank[]> {
  const r = await api.get<QuestionRank[]>('/api/dashboard/rankings/questions', { params: { range, limit } });
  return r.data;
}

export async function getUnitRankings(range = '7d', limit = 10): Promise<UnitRank[]> {
  const r = await api.get<UnitRank[]>('/api/dashboard/rankings/units', { params: { range, limit } });
  return r.data;
}

export async function getTokenTrends(range = '7d'): Promise<DailyTrendPoint[]> {
  const r = await api.get<DailyTrendPoint[]>('/api/dashboard/stats/tokens', { params: { range } });
  return r.data;
}