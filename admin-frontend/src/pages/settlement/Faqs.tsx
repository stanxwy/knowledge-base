import React, { useEffect, useState } from 'react';
import { Card, Empty, Table, Tag } from 'antd';
import { FAQPublished, listPublishedFaqs } from '../../api/settlement';

export const Faqs: React.FC = () => {
  const [items, setItems] = useState<FAQPublished[]>([]);

  useEffect(() => {
    listPublishedFaqs().then(setItems).catch(() => undefined);
  }, []);

  return (
    <Card title="已发布 FAQ">
      {items.length === 0 ? (
        <Empty description="暂无已发布 FAQ" />
      ) : (
        <Table
          rowKey="id"
          dataSource={items}
          pagination={false}
          columns={[
            { title: '问题', dataIndex: 'question', ellipsis: true },
            { title: '答案', dataIndex: 'answer', ellipsis: true },
            {
              title: '分类',
              dataIndex: 'category',
              width: 120,
              render: (c) => (c ? <Tag>{c}</Tag> : '-'),
            },
            {
              title: '命中次数',
              dataIndex: 'hit_count',
              width: 100,
              render: (n) => <Tag color="blue">{n}</Tag>,
            },
            { title: '更新时间', dataIndex: 'updated_at', width: 180 },
          ]}
        />
      )}
    </Card>
  );
};