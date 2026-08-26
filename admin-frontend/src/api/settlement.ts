import { api } from './client';

export interface FAQRecommendation {
  id: number;
  question: string;
  question_pattern: string | null;
  answer: string;
  category: string | null;
  related_unit_id: number | null;
  ask_count: number;
  sample_questions: string[];
  last_asked_at: string | null;
  created_at: string;
}

export interface FAQPublished {
  id: number;
  question: string;
  answer: string;
  category: string | null;
  related_unit_id: number | null;
  hit_count: number;
  created_at: string;
  updated_at: string;
}

export async function listRecommendations(): Promise<FAQRecommendation[]> {
  const r = await api.get<FAQRecommendation[]>('/api/settlement/faqs/recommendations');
  return r.data;
}

export async function listPublishedFaqs(): Promise<FAQPublished[]> {
  const r = await api.get<FAQPublished[]>('/api/settlement/faqs');
  return r.data;
}

export async function reviewFaq(id: number, payload: { action: 'approve' | 'reject'; edited_answer?: string; category?: string }) {
  const r = await api.post(`/api/settlement/faqs/${id}/review`, payload);
  return r.data;
}

export async function createManualFaq(payload: { question: string; answer: string; category?: string; auto_publish?: boolean }) {
  const r = await api.post('/api/settlement/faqs', payload);
  return r.data as FAQPublished;
}

export interface KnowledgeGap {
  id: number;
  question_pattern: string;
  sample_questions: string[];
  ask_count: number;
  last_asked_at: string;
  status: 'unresolved' | 'resolved' | 'ignored';
  resolved_unit_id: number | null;
  created_at: string;
}

export async function listGaps(status?: string): Promise<KnowledgeGap[]> {
  const r = await api.get<KnowledgeGap[]>('/api/settlement/knowledge-gaps', { params: { status } });
  return r.data;
}

export async function updateGap(id: number, status: 'unresolved' | 'resolved' | 'ignored') {
  const r = await api.patch(`/api/settlement/knowledge-gaps/${id}`, { status });
  return r.data;
}

export async function createUnitForGap(id: number, payload: { title: string; content: string; category?: string }) {
  const r = await api.post(`/api/settlement/knowledge-gaps/${id}/create-unit`, payload);
  return r.data;
}

export async function runMineNow(): Promise<{ mined: number; loaded: number }> {
  const r = await api.post('/api/settlement/faqs/_run-mine');
  return r.data;
}