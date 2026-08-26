import React, { useEffect, useState } from 'react';
import { Button, Form, Input, Modal, Popconfirm, Tree, message } from 'antd';
import { DepartmentNode, createDepartment, deleteDepartment, listDepartments, updateDepartment } from '../../api/org';
import { extractErrorMessage } from '../../api/client';

function toTreeData(nodes: DepartmentNode[]): any[] {
  return nodes.map((n) => ({
    key: n.id,
    title: n.name,
    children: n.children?.length ? toTreeData(n.children) : [],
  }));
}

export const Departments: React.FC = () => {
  const [tree, setTree] = useState<DepartmentNode[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<DepartmentNode | null>(null);
  const [parentId, setParentId] = useState<number | null>(null);
  const [form] = Form.useForm();

  const reload = async () => {
    try {
      const r = await listDepartments();
      setTree(r);
    } catch (e) {
      message.error(extractErrorMessage(e));
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const onCreate = () => {
    setEditing(null);
    setParentId(null);
    form.resetFields();
    setModalOpen(true);
  };

  const onAddChild = (parent: DepartmentNode) => {
    setEditing(null);
    setParentId(parent.id);
    form.resetFields();
    setModalOpen(true);
  };

  const onEdit = (node: DepartmentNode) => {
    setEditing(node);
    setParentId(null);
    form.setFieldsValue({ name: node.name, parent_id: node.parent_id, sort_order: node.sort_order });
    setModalOpen(true);
  };

  const onSubmit = async () => {
    try {
      const v = await form.validateFields();
      if (editing) {
        await updateDepartment(editing.id, { name: v.name, sort_order: v.sort_order });
      } else {
        await createDepartment({ name: v.name, parent_id: parentId, sort_order: v.sort_order ?? 0 });
      }
      message.success('已保存');
      setModalOpen(false);
      reload();
    } catch (e: any) {
      if (e?.errorFields) return;
      message.error(extractErrorMessage(e));
    }
  };

  const renderTreeNodes = (data: DepartmentNode[]) =>
    data.map((n) => ({
      key: n.id,
      title: (
        <span>
          {n.name}
          <Button size="small" type="link" onClick={() => onAddChild(n)}>
            + 子部门
          </Button>
          <Button size="small" type="link" onClick={() => onEdit(n)}>
            编辑
          </Button>
          <Popconfirm
            title="确认删除?"
            onConfirm={async () => {
              try {
                await deleteDepartment(n.id);
                reload();
              } catch (e) {
                message.error(extractErrorMessage(e));
              }
            }}
          >
            <Button size="small" type="link" danger>
              删除
            </Button>
          </Popconfirm>
        </span>
      ),
      children: n.children?.length ? renderTreeNodes(n.children) : undefined,
    }));

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={onCreate}>
          新建根部门
        </Button>
      </div>
      <Tree treeData={renderTreeNodes(tree)} defaultExpandAll />

      <Modal
        title={editing ? '编辑部门' : parentId ? '新建子部门' : '新建根部门'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={onSubmit}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="sort_order" label="排序" initialValue={0}>
            <Input type="number" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};