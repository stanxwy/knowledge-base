import React, { useEffect, useState } from 'react';
import { Button, Input, Popconfirm, Select, Space, Table, Tag, message } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { PageResult, batchDeleteUnits, listUnits } from '../../api/knowledge';
import { extractErrorMessage } from '../../api/client';
import type { KnowledgeUnit } from '../../api/knowledge';

export const KnowledgeList: React.FC = () => {
  const [items, setItems] = useState<KnowledgeUnit[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [keyword, setKeyword] = useState('');
  const [status, setStatus] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const reload = async () => {
    setLoading(true);
    try {
      const r: PageResult<KnowledgeUnit> = await listUnits({ page, page_size: pageSize, keyword: keyword || undefined, status });
      setItems(r.items);
      setTotal(r.total);
    } catch (e) {
      message.error(extractErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
  }, [page, pageSize]);

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <Input.Search
          placeholder="搜索标题 / 编码"
          allowClear
          style={{ width: 260 }}
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onSearch={() => { setPage(1); reload(); }}
        />
        <Select
          allowClear
          placeholder="状态"
          style={{ width: 140 }}
          value={status}
          onChange={(v) => { setStatus(v); setPage(1); reload(); }}
          options={[
            { value: 'draft', label: '草稿' },
            { value: 'published', label: '已发布' },
            { value: 'archived', label: '已归档' },
          ]}
        />
        <Button type="primary" onClick={() => navigate('/admin/knowledge/import')}>
          导入新文档
        </Button>
      </div>

      <Table
        rowKey="id"
        loading={loading}
        dataSource={items}
        pagination={{
          current: page, pageSize, total,
          onChange: (p, ps) => { setPage(p); setPageSize(ps); },
        }}
        columns={[
          { title: '编码', dataIndex: 'unit_code', width: 200 },
          { title: '标题', dataIndex: 'title', ellipsis: true },
          { title: '分类', dataIndex: 'category', width: 120 },
          {
            title: '状态',
            dataIndex: 'status',
            width: 90,
            render: (s) => <Tag>{s}</Tag>,
          },
          {
            title: '权限数',
            dataIndex: 'permissions',
            width: 90,
            render: (ps: any[]) => ps?.length ?? 0,
          },
          { title: '更新时间', dataIndex: 'updated_at', width: 180 },
          {
            title: '操作',
            width: 220,
            render: (_, u) => (
                <Space>
                  <Link to={`/admin/knowledge/${u.id}`}>编辑</Link>
                  <Popconfirm
                    title="删除该单元?"
                    onConfirm={async () => {
                      try {
                        await batchDeleteUnits([u.id]);
                        message.success('已删除');
                        reload();
                      } catch (e) {
                        message.error(extractErrorMessage(e));
                      }
                    }}
                  >
                    <a style={{ color: 'red' }}>删除</a>
                  </Popconfirm>
                </Space>
              ),
          },
        ]}
      />
    </div>
  );
};