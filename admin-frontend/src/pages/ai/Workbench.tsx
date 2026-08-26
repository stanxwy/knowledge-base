import React, { useEffect, useRef, useState } from 'react';
import { Alert, Button, Card, Empty, Input, List, Space, Tag, Typography, message } from 'antd';
import { ChatSource, deleteSession, listSessions, streamChat } from '../../api/ai';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAuthStore } from '../../store/auth';

interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
  unauthorized?: number[];
  source?: string;
}

export const Workbench: React.FC = () => {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [sources, setSources] = useState<ChatSource[]>([]);
  const [unauthorized, setUnauthorized] = useState<number[]>([]);
  const [sessions, setSessions] = useState<{ id: string; title: string | null }[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const { user } = useAuthStore();

  useEffect(() => {
    listSessions().then(setSessions).catch(() => undefined);
  }, []);

  const send = async () => {
    if (!input.trim() || busy) return;
    const question = input.trim();
    setInput('');
    setBusy(true);
    setSources([]);
    setUnauthorized([]);

    const userMsg: MessageItem = { id: `u-${Date.now()}`, role: 'user', content: question };
    const assistantId = `a-${Date.now()}`;
    setMessages((prev) => [...prev, userMsg, { id: assistantId, role: 'assistant', content: '' }]);

    const controller = new AbortController();
    abortRef.current = controller;
    let acc = '';

    try {
        await streamChat(
          { question, session_id: currentSession },
          (evt) => {
            if (evt.event === 'recall') {
              // optionally show pending sources
            } else if (evt.event === 'authorized') {
              const ids: number[] = evt.data.unit_ids ?? [];
              setSources((prev) => ids.map((id) => ({ unit_id: id, title: `知识单元 #${id}`, authorized: true })));
            } else if (evt.event === 'unauthorized') {
              const ids: number[] = evt.data.unit_ids ?? [];
              setUnauthorized(ids);
            } else if (evt.event === 'token') {
              acc += evt.data.delta ?? '';
              setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, content: acc } : m)));
            } else if (evt.event === 'done') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: evt.data.answer ?? acc, source: evt.data.source, sources }
                    : m,
                ),
              );
              if (evt.data.session_id) setCurrentSession(evt.data.session_id);
              // refresh session list
              listSessions().then(setSessions).catch(() => undefined);
            } else if (evt.event === 'error') {
              message.error(evt.data.message ?? '请求失败');
            }
          },
          controller.signal,
        );
      } catch (e: any) {
        message.error(e?.message ?? '请求失败');
      } finally {
        setBusy(false);
        abortRef.current = null;
      }
  };

  const stop = () => abortRef.current?.abort();

  const switchSession = async (sid: string) => {
    setCurrentSession(sid);
    setMessages([]);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 16, height: 'calc(100vh - 130px)' }}>
      <Card title="会话" size="small" bodyStyle={{ padding: 0 }}>
        <Button
          block
          type="primary"
          style={{ margin: 8 }}
          onClick={() => {
            setCurrentSession(null);
            setMessages([]);
          }}
        >
          新建会话
        </Button>
        <List
          size="small"
          dataSource={sessions}
          locale={{ emptyText: '暂无会话' }}
          renderItem={(s) => (
            <List.Item
              style={{ padding: '8px 12px', cursor: 'pointer', background: s.id === currentSession ? '#e6f4ff' : undefined }}
              actions={[
                <Button
                  key="x"
                  size="small"
                  type="link"
                  danger
                  onClick={async (e) => {
                    e.stopPropagation();
                    await deleteSession(s.id);
                    setSessions((prev) => prev.filter((x) => x.id !== s.id));
                  }}
                >
                  ×
                </Button>,
              ]}
              onClick={() => switchSession(s.id)}
            >
              <Typography.Text ellipsis style={{ width: 140 }}>
                {s.title || s.id.slice(0, 8)}
              </Typography.Text>
            </List.Item>
          )}
        />
      </Card>

      <Card bodyStyle={{ display: 'flex', flexDirection: 'column', height: '100%', padding: 16 }}>
        <div style={{ flex: 1, overflowY: 'auto', marginBottom: 16 }}>
          {messages.length === 0 && (
            <Empty description="请输入问题,AI 会基于知识库进行回答" style={{ marginTop: 80 }} />
          )}
          {messages.map((m) => (
            <div
              key={m.id}
              style={{
                display: 'flex',
                justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
                marginBottom: 12,
              }}
            >
              <div
                style={{
                  maxWidth: '80%',
                  background: m.role === 'user' ? '#1677ff' : '#f5f5f5',
                  color: m.role === 'user' ? '#fff' : '#333',
                  padding: '10px 14px',
                  borderRadius: 8,
                }}
              >
                <div style={{ whiteSpace: 'pre-wrap' }}>
                  {m.role === 'assistant' ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content || '...'}</ReactMarkdown>
                  ) : (
                    m.content
                  )}
                </div>
                {m.role === 'assistant' && (m.source || sources.length > 0 || unauthorized.length > 0) && (
                  <div style={{ marginTop: 8, borderTop: '1px solid #e8e8e8', paddingTop: 8 }}>
                    {m.source && (
                      <Tag color={m.source === 'faq' ? 'gold' : 'blue'} style={{ marginBottom: 4 }}>
                        来源:{m.source === 'faq' ? 'FAQ 缓存' : 'RAG 检索'}
                      </Tag>
                    )}
                    {sources.map((s) => (
                      <Tag key={s.unit_id} color="green" style={{ marginBottom: 4 }}>
                        #{s.unit_id} {s.title}
                      </Tag>
                    ))}
                    {unauthorized.map((id) => (
                      <Tag key={id} color="red" style={{ marginBottom: 4 }}>
                        ⛔ #{id} 无权访问
                      </Tag>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        <Space.Compact style={{ width: '100%' }}>
          <Input.TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`以 ${user?.display_name ?? user?.username ?? ''} 身份提问...`}
            autoSize={{ minRows: 1, maxRows: 4 }}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            disabled={busy}
          />
          {busy ? (
            <Button danger onClick={stop}>
              停止
            </Button>
          ) : (
            <Button type="primary" onClick={send}>
              发送
            </Button>
          )}
        </Space.Compact>
        {unauthorized.length > 0 && (
          <Alert
            style={{ marginTop: 8 }}
            type="warning"
            showIcon
            message={`检测到 ${unauthorized.length} 条召回内容您无权访问,如需访问请联系管理员`}
          />
        )}
      </Card>
    </div>
  );
};