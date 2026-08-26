import React, { useEffect, useState } from 'react';
import { Button, Form, Input, Modal, Select, Space, Table, Tag, Typography, message } from 'antd';
import { KnowledgeGap, createUnitForGap, listGaps, updateGap } from '../../api/settlement';
import { extractErrorMessage } from '../../api/client';

export const Gaps: React.FC = () => {
  const [items, setItems] = useState<KnowledgeGap[]>([]);
  const [statusFilter, setStatusFilter] = useState<string | undefined>('unresolved');
  const [editing, setEditing] = useState<KnowledgeGap | null>(null);
  const [form] = Form.useForm();

  const reload = async () => {
    try {
      setItems(await listGaps(statusFilter));
    } catch (e) {
      message.error(extractErrorMessage(e));
    }
  };

  useEffect(() => {
    reload();
  }, [statusFilter]);

  const onCreateUnit = (g: KnowledgeGap) => {
    setEditing(g);
    form.resetFields();
    form.setFieldsValue({
      title: g.sample_questions[0] ?? g.question_pattern,
      content: '(待补充)',
    });
  };

  const submitCreateUnit = async () => {
    if (!editing) return;
    try {
      const v = await form.validateFields();
      await createUnitForGap(editing.id, v);
      message.success('已建档');
      setEditing(null);
      reload();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error(extractErrorMessage(e));
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          知识缺口
        </Typography.Title>
        <Select
          value={statusFilter}
          onChange={(v) => setStatusFilter(v)}
          style={{ width: 160 }}
          options={[
            { value: 'unresolved', label: '未解决' },
            { value: 'resolved', label: '已解决' },
            { value: 'ignored', label: '已忽略' },
          ]}
        />
      </Space>
      <Table
        rowKey="id"
        dataSource={items}
        columns={[
          { title: '问题模式', dataIndex: 'question_pattern', ellipsis: true },
          { title: '样本', dataIndex: 'sample_questions', render: (s: string[]) => <Tag>{s[0] ?? '-'}</Tag> },
          { title: '频次', dataIndex: 'ask_count', width: 80, render: (n) => <Tag color="orange">{n}</Tag> },
          {
            title: '状态',
            dataIndex: 'status',
            width: 90,
            render: (s) =>
              s === 'unresolved' ? <Tag color="red">未解决</Tag> : s === 'resolved' ? <Tag color="green">已解决</Tag> : <Tag>已忽略</Tag>,
          },
          { title: '最近提问', dataIndex: 'last_asked_at', width: 180 },
          {
            title: '操作',
            width: 280,
            render: (_, g) => (
              <Space>
                <Button size="small" type="primary" onClick={() => onCreateUnit(g)} disabled={g.status === 'resolved'}>
                  一键建档
                </Button>
                <Button
                  size="small"
                  onClick={async () => {
                    await updateGap(g.id, 'ignored');
                    reload();
                  }}
                >
                  忽略
                </Button>
              </Space>
            ),
          },
        ]}
      />

      <Modal
        open={!!editing}
        title={`为缺口 ${editing?.question_pattern} 建档`}
        onCancel={() => setEditing(null)}
        onOk={submitCreateUnit}
        okText="建档"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="知识单元标题" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="content" label="正文内容" rules={[{ required: true }]}>
            <Input.TextArea rows={6} />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};