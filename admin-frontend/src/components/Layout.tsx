import React from 'react';
import { Layout as AntLayout, Menu, Avatar, Dropdown, Typography, Tag } from 'antd';
import {
  DashboardOutlined,
  TeamOutlined,
  ApartmentOutlined,
  SafetyCertificateOutlined,
  BookOutlined,
  CloudUploadOutlined,
  RobotOutlined,
  BulbOutlined,
  AuditOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/auth';

const { Header, Sider, Content } = AntLayout;

interface MenuConfig {
  key: string;
  label: string;
  icon: React.ReactNode;
  permission?: string;
}

const MENUS: MenuConfig[] = [
  { key: '/admin/dashboard', label: '数据看板', icon: <DashboardOutlined />, permission: 'dashboard:read' },
  { key: '/admin/org', label: '组织与权限', icon: <TeamOutlined /> },
  { key: '/admin/org/users', label: '用户管理', icon: <UserOutlined />, permission: 'user:read' },
  { key: '/admin/org/departments', label: '部门管理', icon: <ApartmentOutlined />, permission: 'org:read' },
  { key: '/admin/org/roles', label: '角色权限', icon: <SafetyCertificateOutlined />, permission: 'role:read' },
  { key: '/admin/knowledge', label: '知识维护', icon: <BookOutlined />, permission: 'knowledge:read' },
  { key: '/admin/knowledge/import', label: '知识导入', icon: <CloudUploadOutlined />, permission: 'knowledge:import' },
  { key: '/admin/ai', label: 'AI 对话工作台', icon: <RobotOutlined />, permission: 'ai:access' },
  { key: '/admin/settlement/faqs/review', label: 'FAQ 审核', icon: <BulbOutlined />, permission: 'settlement:read' },
  { key: '/admin/settlement/faqs', label: '已发布 FAQ', icon: <BulbOutlined />, permission: 'settlement:read' },
  { key: '/admin/settlement/gaps', label: '知识缺口', icon: <AuditOutlined />, permission: 'settlement:read' },
];

export const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, permissions, clear } = useAuthStore();
  const is_superuser = user?.is_superuser ?? false;

  const items = MENUS.filter((m) => {
    if (!m.permission) return true;
    if (is_superuser) return true;
    return permissions.includes(m.permission);
  }).map((m) => ({
    key: m.key,
    icon: m.icon,
    label: <Link to={m.key}>{m.label}</Link>,
  }));

  const selectedKey = items.find((m) => location.pathname.startsWith(m.key))?.key ?? '/admin/dashboard';

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="dark">
        <div style={{ padding: '16px', color: '#fff', textAlign: 'center', borderBottom: '1px solid #1f1f1f' }}>
          <Typography.Title level={4} style={{ color: '#fff', margin: 0 }}>KBMS</Typography.Title>
          <Typography.Text type="secondary" style={{ color: '#aaa', fontSize: 12 }}>
            Knowledge Base Management
          </Typography.Text>
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[selectedKey]} items={items} />
      </Sider>
      <AntLayout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f0f0f0' }}>
          <Typography.Title level={4} style={{ margin: 0 }}>
            {MENUS.find((m) => m.key === selectedKey)?.label ?? 'KBMS'}
          </Typography.Title>
          <Dropdown
            menu={{
              items: [
                {
                  key: 'logout',
                  icon: <LogoutOutlined />,
                  label: '退出登录',
                  onClick: () => {
                    clear();
                    navigate('/admin/login');
                  },
                },
              ],
            }}
          >
            <span style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} style={{ marginRight: 8 }} />
              <span>{user?.display_name ?? user?.username ?? '匿名'}</span>
              {is_superuser && <Tag color="gold" style={{ marginLeft: 8 }}>超级管理员</Tag>}
            </span>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: '#fff', borderRadius: 8 }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
};