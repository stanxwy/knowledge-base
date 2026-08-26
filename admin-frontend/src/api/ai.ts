import { api } from './client';

export interface ChatEvent {
  event: 'recall' | 'authorized' | 'unauthorized' | 'token' | 'done' | 'error';
  data: any;
}

export interface ChatSource {
  unit_id: number;
  unit_code?: string;
  title: string;
  score?: number;
  authorized: boolean;
}

export async function streamChat(
  payload: { question: string; session_id?: string | null },
  onEvent: (evt: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const r = await fetch('/api/ai/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(payload),
    signal,
  });
  if (!r.body) throw new Error('No response body');
  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const block = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const lines = block.split('\n');
      let eventName = 'message';
      let dataLines: string[] = [];
      for (const line of lines) {
        if (line.startsWith('event:')) eventName = line.slice(6).trim();
        else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim());
      }
      if (dataLines.length === 0) continue;
      try {
        const data = JSON.parse(dataLines.join('\n'));
        onEvent({ event: eventName as ChatEvent['event'], data });
      } catch (e) {
        // ignore malformed frame
      }
    }
  }
}

export interface SessionSummary {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export async function listSessions(): Promise<SessionSummary[]> {
  const r = await api.get<SessionSummary[]>('/api/ai/sessions');
  return r.data;
}

export async function deleteSession(id: string) {
  await api.delete(`/api/ai/sessions/${id}`);
}