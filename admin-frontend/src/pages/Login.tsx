import React, { useState } from 'react';
import { Button, Card, Form, Input, message, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import { useAuthStore } from '../store/auth';

export const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setTokens, setIdentity } = useAuthStore();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const r = await login(values.username, values.password);
      setTokens(r.access_token, r.refresh_token);
      setIdentity({
        user_info: r.user_info,
        roles: [],
        permissions: r.permissions,
      });
      message.success('登录成功');
      navigate('/admin/dashboard', { replace: true });
    } catch (e: any) {
      message.error(e?.response?.data?.error?.message ?? '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f2f5' }}>
      <Card style={{ width: 380 }}>
        <Typography.Title level={3} style={{ textAlign: 'center', marginBottom: 24 }}>
          KBMS Admin
        </Typography.Title>
        <Form layout="vertical" onFinish={onFinish} initialValues={{ username: 'admin', password: 'admin123' }}>
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input autoComplete="username" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password autoComplete="current-password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
          <Typography.Paragraph type="secondary" style={{ fontSize: 12, textAlign: 'center', marginBottom: 0 }}>
            初始账号 admin / admin123(请在生产环境修改)
          </Typography.Paragraph>
        </Form>
      </Card>
    </div>
  );
};