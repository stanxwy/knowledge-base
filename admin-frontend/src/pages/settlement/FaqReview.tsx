import React, { useEffect, useState } from 'react';
import { Button, Card, Empty, Input, Modal, Space, Table, Tag, Typography, message } from 'antd';
import { FAQRecommendation, listRecommendations, reviewFaq, runMineNow } from '../../api/settlement';
import { extractErrorMessage } from '../../api/client';

export const FaqReview: React.FC = () => {
  const [items, setItems] = useState<FAQRecommendation[]>([]);
  const [editing, setEditing] = useState<FAQRecommendation | null>(null);
  const [answer, setAnswer] = useState('');
  const [category, setCategory] = useState('');
  const [running, setRunning] = useState(false);

  const reload = async () => {
    try {
      setItems(await listRecommendations());
    } catch (e) {
      message.error(extractErrorMessage(e));
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const onMine = async () => {
    setRunning(true);
    try {
      const r = await runMineNow();
      message.success(`挖出 ${r.mined} 条新候选,加载 ${r.loaded} 条已发布到缓存`);
      reload();
    } catch (e) {
      message.error(extractErrorMessage(e));
    } finally {
      setRunning(false);
    }
  };

  const openReview = (rec: FAQRecommendation) => {
    setEditing(rec);
    setAnswer(rec.answer);
    setCategory(rec.category ?? '');
  };

  const submit = async (action: 'approve' | 'reject') => {
    if (!editing) return;
    try {
      await reviewFaq(editing.id, { action, edited_answer: answer, category: category || undefined });
      message.success(action === 'approve' ? '已发布' : '已驳回');
      setEditing(null);
      reload();
    } catch (e) {
      message.error(extractErrorMessage(e));
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          FAQ 候选审核
        </Typography.Title>
        <Button type="primary" loading={running} onClick={onMine}>
          立即挖掘
        </Button>
      </Space>
      {items.length === 0 ? (
        <Empty description="暂无待审核候选,试试点击" />
      ) : (
        <Table
          rowKey="id"
          dataSource={items}
          columns={[
            { title: '问题', dataIndex: 'question', ellipsis: true },
            {
              title: '频次',
              dataIndex: 'ask_count',
              width: 90,
              render: (n) => <Tag color="blue">{n}</Tag>,
            },
            {
              title: '关联单元',
              dataIndex: 'related_unit_id',
              width: 120,
              render: (id) => (id ? <Tag>#{id}</Tag> : <Tag>无</Tag>),
            },
            { title: '建议答案', dataIndex: 'answer', ellipsis: true },
            {
              title: '操作',
              width: 140,
              render: (_, rec) => <Button onClick={() => openReview(rec)}>审核</Button>,
            },
          ]}
        />
      )}

      <Modal
        open={!!editing}
        title={editing?.question}
        onCancel={() => setEditing(null)}
        footer={null}
        width={720}
      >
        <Typography.Paragraph type="secondary">
          候选来自历史问答聚合(频次 ≥ 阈值),确认无误后可发布为标准答案,后续提问自动命中。
        </Typography.Paragraph>
        <Input.TextArea
          rows={6}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          style={{ marginBottom: 8 }}
        />
        <Input
          placeholder="分类 (可选,例如: 家电维修)"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={{ marginBottom: 16 }}
        />
        <Space>
          <Button type="primary" onClick={() => submit('approve')}>
            通过并发布
          </Button>
          <Button danger onClick={() => submit('reject')}>
            驳回
          </Button>
        </Space>
      </Modal>
    </div>
  );
};