import React, { useEffect, useState } from 'react';
import { Button, Card, Progress, Space, Upload, message } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { ImportTaskStatus, importFiles, pollImportTask } from '../../api/knowledge';
import { extractErrorMessage } from '../../api/client';

export const KnowledgeImport: React.FC = () => {
  const [fileList, setFileList] = useState<File[]>([]);
  const [task, setTask] = useState<ImportTaskStatus | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!task) return;
    const timer = setInterval(async () => {
      try {
        const r = await pollImportTask(task.task_id);
        setTask(r);
        if (r.status === 'done' || r.status === 'failed' || r.status === 'timeout') {
          clearInterval(timer);
        }
      } catch (e) {
        clearInterval(timer);
      }
    }, 1500);
    return () => clearInterval(timer);
  }, [task?.task_id]);

  const onSubmit = async () => {
    if (!fileList.length) {
      message.warning('请选择文件');
      return;
    }
    setSubmitting(true);
    try {
      const t = await importFiles(fileList);
      setTask(t);
      message.success('已提交,正在上传至RAG引擎');
    } catch (e) {
      message.error(extractErrorMessage(e));
    } finally {
      setSubmitting(false);
    }
  };

  const progressPct = task
    ? Math.round(
        (task.files.filter((f) => f.status === 'done' || f.status === 'failed').length / task.files.length) * 100,
      )
    : 0;

  return (
    <div>
      <Card>
        <Upload.Dragger
          multiple
          accept=".pdf,.docx,.markdown,.md,.txt"
          fileList={fileList.map((f) => ({ uid: f.name, name: f.name, status: 'done' }))}
          beforeUpload={(file) => {
            setFileList((prev) => [...prev, file]);
            return false; // Prevent automatic upload
          }}
          onRemove={(file) => {
            setFileList((prev) => prev.filter((f) => f.name !== file.name));
          }}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p>点击或拖拽 PDF / Word / Markdown / TXT 文件到此区域上传</p>
        </Upload.Dragger>
        <Space style={{ marginTop: 16 }}>
          <Button type="primary" loading={submitting} onClick={onSubmit}>
            提交导入
          </Button>
          <Button onClick={() => setFileList([])}>清空</Button>
        </Space>
      </Card>

      {task && (
        <Card title={`导入任务 ${task.task_id.slice(0, 8)}...`} style={{ marginTop: 16 }}>
          <Progress percent={progressPct} status={task.status === 'failed' ? 'exception' : task.status === 'timeout' ? 'exception' : undefined} />
          <div style={{ marginTop: 16 }}>
            {task.files.map((f) => (
              <div key={f.filename} style={{ marginBottom: 8 }}>
                <strong>{f.filename}</strong>: {f.status}
                {f.status === 'done' && (
                  <span style={{ marginLeft: 8, color: '#52c41a' }}>
                    → 已上传，RAG处理完成
                  </span>
                )}
                {f.status === 'uploaded' && (
                  <span style={{ marginLeft: 8, color: '#1890ff' }}>
                    → 已上传，等待RAG处理
                  </span>
                )}
                {f.message && <span style={{ marginLeft: 8, color: '#8c8c8c' }}>({f.message})</span>}
                {f.error && <span style={{ color: 'red', marginLeft: 8 }}>{f.error}</span>}
              </div>
            ))}
          </div>
          {(task.status === 'done' || task.status === 'timeout') && (
            <Button type="primary" onClick={() => navigate('/admin/knowledge')}>
              查看知识单元列表
            </Button>
          )}
        </Card>
      )}
    </div>
  );
};