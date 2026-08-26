import React, { useEffect, useState } from 'react';
import { Button, Form, Input, message, Modal, Popconfirm, Switch as ASwitch, Table, Tag } from 'antd';
import { PageResult, UserDetail, createUser, deleteUser, listRoles, listUsers, resetPassword, toggleUserStatus, updateUser } from '../../api/org';
import { extractErrorMessage } from '../../api/client';
import type { Role } from '../../api/org';

export const Users: React.FC = () => {
  const [items, setItems] = useState<UserDetail[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [keyword, setKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [roles, setRoles] = useState<Role[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<UserDetail | null>(null);
  const [form] = Form.useForm();

  const reload = async () => {
    setLoading(true);
    try {
      const r: PageResult<UserDetail> = await listUsers({ page, page_size: pageSize, keyword: keyword || undefined });
      setItems(r.items);
      setTotal(r.total);
    } catch (e) {
      message.error(extractErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    listRoles().then(setRoles).catch(() => undefined);
  }, []);

  useEffect(() => {
    reload();
  }, [page, pageSize]);

  const onSearch = () => {
    setPage(1);
    reload();
  };

  const onCreate = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const onEdit = (u: UserDetail) => {
    setEditing(u);
    form.setFieldsValue({
      display_name: u.display_name,
      email: u.email ?? undefined,
      department_id: u.department_id ?? undefined,
      role_ids: u.roles.map((r) => r.id),
      status: u.status,
    });
    setModalOpen(true);
  };

  const onSubmit = async () => {
    try {
      const v = await form.validateFields();
      if (editing) {
        await updateUser(editing.id, {
          display_name: v.display_name,
          email: v.email,
          department_id: v.department_id,
          role_ids: v.role_ids,
          status: v.status,
        });
        message.success('已更新');
      } else {
        await createUser({
          username: v.username,
          password: v.password,
          display_name: v.display_name,
          email: v.email,
          department_id: v.department_id,
          role_ids: v.role_ids ?? [],
          status: v.status ?? 1,
        });
        message.success('已创建');
      }
      setModalOpen(false);
      reload();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error(extractErrorMessage(e));
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <Input.Search
          placeholder="按用户名 / 姓名搜索"
          allowClear
          style={{ width: 280 }}
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onSearch={onSearch}
        />
        <Button type="primary" onClick={onCreate}>
          新建用户
        </Button>
      </div>
      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        pagination={{
          current: page,
          pageSize,
          total,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
          },
        }}
        columns={[
          { title: 'ID', dataIndex: 'id', width: 60 },
          { title: '用户名', dataIndex: 'username' },
          { title: '姓名', dataIndex: 'display_name' },
          {
            title: '部门',
            dataIndex: 'department',
            render: (d) => (d ? d.name : <Tag color="default">未分配</Tag>),
          },
          {
            title: '角色',
            dataIndex: 'roles',
            render: (rs: Role[]) => (
              <>
                {rs.map((r) => (
                  <Tag color="blue" key={r.id}>
                    {r.role_name}
                  </Tag>
                ))}
              </>
            ),
          },
          {
            title: '状态',
            dataIndex: 'status',
            width: 80,
            render: (s) => (s === 1 ? <Tag color="success">启用</Tag> : <Tag>停用</Tag>),
          },
          {
            title: '操作',
            width: 280,
            render: (_, u) => (
              <>
                <Button size="small" onClick={() => onEdit(u)} style={{ marginRight: 8 }}>
                  编辑
                </Button>
                <Popconfirm
                  title="重置密码?"
                  onConfirm={async () => {
                    try {
                      const r = await resetPassword(u.id);
                      Modal.info({ title: '新密码', content: r.new_password });
                    } catch (e) {
                      message.error(extractErrorMessage(e));
                    }
                  }}
                >
                  <Button size="small" style={{ marginRight: 8 }}>
                    重置密码
                  </Button>
                </Popconfirm>
                <Popconfirm
                  title="切换状态?"
                  onConfirm={async () => {
                    await toggleUserStatus(u.id);
                    reload();
                  }}
                >
                  <Button size="small" style={{ marginRight: 8 }}>
                    {u.status === 1 ? '停用' : '启用'}
                  </Button>
                </Popconfirm>
                <Popconfirm
                  title="确认删除?"
                  onConfirm={async () => {
                    try {
                      await deleteUser(u.id);
                      message.success('已删除');
                      reload();
                    } catch (e) {
                      message.error(extractErrorMessage(e));
                    }
                  }}
                >
                  <Button size="small" danger>
                    删除
                  </Button>
                </Popconfirm>
              </>
            ),
          },
        ]}
      />

      <Modal
        title={editing ? `编辑用户 #${editing.id}` : '新建用户'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={onSubmit}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          {!editing && (
            <>
              <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="password" label="密码" rules={[{ required: true, min: 6 }]}>
                <Input.Password />
              </Form.Item>
            </>
          )}
          <Form.Item name="display_name" label="姓名" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input />
          </Form.Item>
          <Form.Item name="department_id" label="部门ID">
            <Input type="number" placeholder="可选,部门树形 ID" />
          </Form.Item>
          <Form.Item name="role_ids" label="角色" rules={[{ required: true, type: 'array', min: 1, message: '至少选择一个角色' }]}>
            <SelectMulti
              options={roles.map((r) => ({ value: r.id, label: `${r.role_name} (${r.role_code})` }))}
            />
          </Form.Item>
          {!editing && (
            <Form.Item name="status" label="状态" initialValue={1}>
              <ASwitch checkedChildren="启用" unCheckedChildren="停用" defaultChecked />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

import { Select } from 'antd';
const SelectMulti = Select<{ value: number; label: string }[]>.mode;