import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Users } from './pages/org/Users';
import { Departments } from './pages/org/Departments';
import { Roles } from './pages/org/Roles';
import { KnowledgeList } from './pages/knowledge/List';
import { KnowledgeEdit } from './pages/knowledge/Edit';
import { KnowledgeImport } from './pages/knowledge/Import';
import { Workbench } from './pages/ai/Workbench';
import { FaqReview } from './pages/settlement/FaqReview';
import { Faqs } from './pages/settlement/Faqs';
import { Gaps } from './pages/settlement/Gaps';
import { useAuthStore } from './store/auth';
import { fetchMe } from './api/auth';
import { useEffect, useState } from 'react';
import { Spin } from 'antd';

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { accessToken, setIdentity, clear } = useAuthStore();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    if (!accessToken) {
      setReady(true);
      return;
    }
    (async () => {
      try {
        const me = await fetchMe();
        if (!cancelled) setIdentity(me);
      } catch {
        if (!cancelled) clear();
      } finally {
        if (!cancelled) setReady(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [accessToken, clear, setIdentity]);

  if (!ready) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin />
      </div>
    );
  }
  if (!accessToken) return <Navigate to="/admin/login" replace />;
  return <>{children}</>;
}

export const router = createBrowserRouter([
  {
    path: '/admin/login',
    element: <Login />,
  },
  {
    path: '/admin',
    element: (
      <RequireAuth>
        <Layout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/admin/dashboard" replace /> },
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'org/users', element: <Users /> },
      { path: 'org/departments', element: <Departments /> },
      { path: 'org/roles', element: <Roles /> },
      { path: 'knowledge', element: <KnowledgeList /> },
      { path: 'knowledge/import', element: <KnowledgeImport /> },
      { path: 'knowledge/:id', element: <KnowledgeEdit /> },
      { path: 'ai', element: <Workbench /> },
      { path: 'settlement/faqs', element: <Faqs /> },
      { path: 'settlement/faqs/review', element: <FaqReview /> },
      { path: 'settlement/gaps', element: <Gaps /> },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/admin" replace />,
  },
]);