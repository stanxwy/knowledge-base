import React, { useEffect, useState } from 'react';
import { Button, Checkbox, Form, Input, Modal, Table, Tag, message } from 'antd';
import { PermissionEntry, Role, createRole, listPermissions, listRoles, replaceRolePermissions } from '../../api/org';
import { extractErrorMessage } from '../../api/client';

export const Roles: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [perms, setPerms] = useState<PermissionEntry[]>([]);
  const [editing, setEditing] = useState<Role | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [form] = Form.useForm();
  const [createForm] = Form.useForm();

  const reload = async () => {
    try {
      const [rs, ps] = await Promise.all([listRoles(), listPermissions()]);
      setRoles(rs);
      setPerms(ps);
    } catch (e) {
      message.error(extractErrorMessage(e));
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const onEditPerms = (role: Role) => {
    setEditing(role);
    setSelected(role.permissions);
  };

  const onSavePerms = async () => {
    if (!editing) return;
    try {
      await replaceRolePermissions(editing.id, selected);
      message.success('已保存');
      setEditing(null);
      reload();
    } catch (e) {
      message.error(extractErrorMessage(e));
    }
  };

  const onCreate = async () => {
    try {
      const v = await createForm.validateFields();
      await createRole({ role_name: v.role_name, role_code: v.role_code, description: v.description });
      message.success('已创建');
      setCreateOpen(false);
      createForm.resetFields();
      reload();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error(extractErrorMessage(e));
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={() => setCreateOpen(true)}>
          新建角色
        </Button>
      </div>
      <Table
        rowKey="id"
        dataSource={roles}
        columns={[
          { title: '编码', dataIndex: 'role_code', width: 180 },
          { title: '名称', dataIndex: 'role_name' },
          { title: '描述', dataIndex: 'description' },
          {
            title: '内置',
            dataIndex: 'is_builtin',
            width: 80,
            render: (b) => (b ? <Tag color="gold">内置</Tag> : <Tag>自定义</Tag>),
          },
          {
            title: '权限码数',
            dataIndex: 'permissions',
            width: 100,
            render: (ps: string[]) => <Tag color="blue">{ps.length}</Tag>,
          },
          {
            title: '操作',
            width: 120,
            render: (_, r) => <Button onClick={() => onEditPerms(r)}>编辑权限</Button>,
          },
        ]}
      />

      <Modal
        title={editing ? `编辑权限 - ${editing.role_name}` : ''}
        open={!!editing}
        onCancel={() => setEditing(null)}
        onOk={onSavePerms}
        width={560}
        okText="保存"
        cancelText="取消"
      >
        <Checkbox.Group value={selected} onChange={(v) => setSelected(v as string[])} style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
          {perms.map((p) => (
            <Checkbox key={p.id} value={p.permission_code}>
              {p.permission_code}
            </Checkbox>
          ))}
        </Checkbox.Group>
      </Modal>

      <Modal
        title="新建角色"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onOk={onCreate}
        okText="保存"
        cancelText="取消"
      >
        <Form form={createForm} layout="vertical">
          <Form.Item name="role_code" label="角色编码" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="role_name" label="角色名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};