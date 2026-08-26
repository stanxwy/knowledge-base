import React, { useEffect, useState } from 'react';
import { Button, Form, Input, Modal, Select, Space, Tag, Typography, message } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { KnowledgeUnit, UnitPermission, getUnit, replaceUnitPermissions, updateUnit } from '../../api/knowledge';
import { extractErrorMessage } from '../../api/client';

const TARGET_TYPES: Array<{ value: UnitPermission['target_type']; label: string }> = [
  { value: 'global', label: '全局公开' },
  { value: 'department', label: '部门' },
  { value: 'role', label: '角色' },
  { value: 'user', label: '个人' },
];

export const KnowledgeEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [unit, setUnit] = useState<KnowledgeUnit | null>(null);
  const [perms, setPerms] = useState<UnitPermission[]>([]);
  const [form] = Form.useForm();
  const [permForm] = Form.useForm();

  const reload = async () => {
    if (!id) return;
    try {
      const u = await getUnit(Number(id));
      setUnit(u);
      setPerms(u.permissions ?? []);
      form.setFieldsValue({
        title: u.title,
        content: u.content,
        summary: u.summary,
        category: u.category,
        tags: u.tags,
        status: u.status,
      });
    } catch (e) {
      message.error(extractErrorMessage(e));
    }
  };

  useEffect(() => {
    reload();
  }, [id]);

  const onSave = async () => {
    try {
      const v = await form.validateFields();
      await updateUnit(Number(id), v);
      message.success('已保存');
      reload();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error(extractErrorMessage(e));
    }
  };

  const onSavePerms = async () => {
    try {
      const v = await permForm.validateFields();
      const list: UnitPermission[] = (v.entries ?? []).map((e: any) => ({
        target_type: e.target_type,
        target_id: e.target_type === 'global' ? null : e.target_id,
      }));
      await replaceUnitPermissions(Number(id), list);
      message.success('权限已保存');
      reload();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error(extractErrorMessage(e));
    }
  };

  if (!unit) return null;

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button onClick={() => navigate('/admin/knowledge')}>返回</Button>
        <Typography.Title level={3} style={{ margin: 0 }}>
          {unit.unit_code}
        </Typography.Title>
        <Tag color="blue">{unit.status}</Tag>
      </Space>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
        <div style={{ background: '#fff', padding: 24, borderRadius: 8 }}>
          <Form form={form} layout="vertical">
            <Form.Item name="title" label="标题" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="summary" label="摘要">
              <Input.TextArea rows={2} />
            </Form.Item>
            <Form.Item name="content" label="正文" rules={[{ required: true }]}>
              <Input.TextArea rows={10} />
            </Form.Item>
            <Form.Item name="category" label="分类">
              <Input />
            </Form.Item>
            <Form.Item name="tags" label="标签">
              <Select mode="tags" tokenSeparators={[',']} />
            </Form.Item>
            <Form.Item name="status" label="状态">
              <Select
                options={[
                  { value: 'draft', label: '草稿' },
                  { value: 'published', label: '已发布' },
                  { value: 'archived', label: '已归档' },
                ]}
              />
            </Form.Item>
            <Button type="primary" onClick={onSave}>
              保存
            </Button>
          </Form>
        </div>

        <div style={{ background: '#fff', padding: 24, borderRadius: 8 }}>
          <Typography.Title level={4}>数据权限</Typography.Title>
          <Typography.Paragraph type="secondary">
            混合配置全局 / 部门 / 角色 / 个人,满足任意一种即可访问。空配置 = 默认拒绝。
          </Typography.Paragraph>
          <Form form={permForm} layout="vertical" initialValues={{ entries: permFormat(perms) }}>
            <Form.List name="entries">
              {(fields, { add, remove }) => (
                <>
                  {fields.map((field) => (
                    <Space key={field.key} align="baseline" style={{ display: 'flex', marginBottom: 8 }}>
                      <Form.Item name={[field.name, 'target_type']} rules={[{ required: true }]}>
                        <Select style={{ width: 140 }} options={TARGET_TYPES} />
                      </Form.Item>
                      <Form.Item name={[field.name, 'target_id']}>
                        <Input type="number" placeholder="target_id" style={{ width: 140 }} />
                      </Form.Item>
                      <Button onClick={() => remove(field.name)} danger>
                        移除
                      </Button>
                    </Space>
                  ))}
                  <Button onClick={() => add({ target_type: 'global' })} block>
                    + 添加权限
                  </Button>
                </>
              )}
            </Form.List>
            <Button type="primary" onClick={onSavePerms} style={{ marginTop: 16 }}>
              保存权限
            </Button>
          </Form>
        </div>
      </div>
    </div>
  );
};

function permFormat(ps: UnitPermission[]) {
  return ps.map((p) => ({ target_type: p.target_type, target_id: p.target_id }));
}