import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Segmented, Spin, Table, Typography } from 'antd';
import {
  DashboardMetrics,
  DailyTrendPoint,
  QuestionRank,
  UnitRank,
  getMetrics,
  getQuestionRankings,
  getTokenTrends,
  getUnitRankings,
} from '../api/dashboard';
import { Line } from '@ant-design/charts';

type Range = 'today' | '7d' | '30d' | 'all';

export const Dashboard: React.FC = () => {
  const [range, setRange] = useState<Range>('7d');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [questions, setQuestions] = useState<QuestionRank[]>([]);
  const [units, setUnits] = useState<UnitRank[]>([]);
  const [trends, setTrends] = useState<DailyTrendPoint[]>([]);
  const [loading, setLoading] = useState(false);

  const reload = async (r: Range) => {
    setLoading(true);
    try {
      const [m, q, u, t] = await Promise.all([
        getMetrics(r),
        getQuestionRankings(r, 10),
        getUnitRankings(r, 10),
        getTokenTrends(r),
      ]);
      setMetrics(m);
      setQuestions(q);
      setUnits(u);
      setTrends(t);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload(range);
  }, [range]);

  return (
    <Spin spinning={loading}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          数据看板
        </Typography.Title>
        <Segmented<Range>
          value={range}
          onChange={(v) => setRange(v as Range)}
          options={[
            { label: '今日', value: 'today' },
            { label: '7 天', value: '7d' },
            { label: '30 天', value: '30d' },
            { label: '全部', value: 'all' },
          ]}
        />
      </div>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <MetricCard title="访问次数" value={metrics?.total_visits ?? 0} />
        <MetricCard title="独立访问人数" value={metrics?.unique_visitors ?? 0} />
        <MetricCard title="知识单元总数" value={metrics?.total_knowledge_units ?? 0} />
        <MetricCard title="总 Token 消耗" value={metrics?.total_tokens.toLocaleString() ?? 0} />
        <MetricCard title="平均响应时间(ms)" value={metrics?.avg_response_time_ms ?? 0} />
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          <Card title="访问 / Token / 响应时间趋势" style={{ marginBottom: 16 }}>
            <Line
              data={trends.flatMap((t) => [
                { date: t.date, type: '访问', value: t.visits },
                { date: t.date, type: 'Token / 100', value: Math.round(t.total_tokens / 100) },
                { date: t.date, type: '响应 ms / 100', value: Math.round(t.avg_response_time_ms / 100) },
              ])}
              xField="date"
              yField="value"
              colorField="type"
              height={260}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="常见问题 TOP 榜">
            <Table
              rowKey="question_pattern"
              dataSource={questions}
              size="small"
              pagination={false}
              columns={[
                { title: '问题', dataIndex: 'question_pattern', ellipsis: true },
                { title: '次数', dataIndex: 'ask_count', width: 80 },
              ]}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="知识单元热度榜">
            <Table
              rowKey="unit_id"
              dataSource={units}
              size="small"
              pagination={false}
              columns={[
                { title: '编码', dataIndex: 'unit_code', width: 160 },
                { title: '标题', dataIndex: 'title', ellipsis: true },
                { title: '提及', dataIndex: 'mention_count', width: 80 },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </Spin>
  );
};

const MetricCard: React.FC<{ title: string; value: number | string }> = ({ title, value }) => (
  <Col span={Math.floor(24 / 5)}>
    <Card>
      <Typography.Text type="secondary">{title}</Typography.Text>
      <div style={{ fontSize: 28, fontWeight: 600, color: '#1677ff' }}>{value}</div>
    </Card>
  </Col>
);