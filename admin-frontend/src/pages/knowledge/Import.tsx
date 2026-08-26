import React, { useEffect, useState } from 'react';
import { Button, Card, Progress, Space, Upload, message, Collapse, Tag } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { ImportTaskStatus, importFiles, pollImportTask, pollAppTaskProgress } from '../../api/knowledge';
import { extractErrorMessage } from '../../api/client';

const { Panel } = Collapse;

export const KnowledgeImport: React.FC = () => {
  const [fileList, setFileList] = useState<File[]>([]);
  const [task, setTask] = useState<ImportTaskStatus | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!task) return;

    // Poll both admin task store and app task progress
    const timer = setInterval(async () => {
      try {
        // Poll admin task store for file status updates
        const adminTask = await pollImportTask(task.task_id);
        setTask(adminTask);

        // Also poll app for real-time step progress (done_list, running_list)
        // Check if any file has been uploaded to RAG (status='uploaded' or 'processing')
        const hasUploadedFile = adminTask.files.some(f =>
          f.status === 'uploaded' || f.status === 'processing' || f.status === 'done'
        );
        if (hasUploadedFile) {
          try {
            // Poll app task progress using admin task_id (they're linked)
            const appProgress = await pollAppTaskProgress(task.task_id);
            // Update task with app's done_list and running_list
            setTask(prev => prev ? {
              ...prev,
              files: prev.files.map(f => ({
                ...f,
                done_list: appProgress.done_list,
                running_list: appProgress.running_list,
              })),
            } : null);
          } catch (e) {
            // App progress polling may fail if RAG is unavailable, ignore
          }
        }

        if (adminTask.status === 'done' || adminTask.status === 'failed' || adminTask.status === 'timeout') {
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'done':
        return '#52c41a';
      case 'processing':
      case 'uploaded':
        return '#1890ff';
      case 'failed':
        return '#ff4d4f';
      case 'timeout':
        return '#faad14';
      default:
        return '#d9d9d9';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '等待中';
      case 'parsing':
        return '解析中';
      case 'ingesting':
        return '导入中';
      case 'uploaded':
        return '已上传';
      case 'processing':
        return '处理中';
      case 'done':
        return '完成';
      case 'failed':
        return '失败';
      case 'timeout':
        return '超时';
      default:
        return status;
    }
  };

  const renderStepProgress = (file: any) => {
    const totalSteps = file.done_list?.length + file.running_list?.length || 0;
    if (totalSteps === 0) return null;

    const completedSteps = file.done_list?.length || 0;
    const progress = Math.round((completedSteps / totalSteps) * 100);

    return (
      <div style={{ marginTop: 12 }}>
        <div style={{ marginBottom: 8, fontSize: '12px', color: '#8c8c8c' }}>
          处理进度: {completedSteps} / {totalSteps} 步骤
        </div>
        <Progress
          percent={progress}
          size="small"
          status={file.status === 'failed' ? 'exception' : file.status === 'timeout' ? 'exception' : 'active'}
          strokeColor={getStatusColor(file.status)}
        />

        {(file.done_list?.length > 0 || file.running_list?.length > 0) ? (
          <Collapse
            size="small"
            style={{ marginTop: 8 }}
            items={[
              {
                key: '1',
                label: `查看步骤详情 (已完成: ${file.done_list?.length || 0}, 进行中: ${file.running_list?.length || 0})`,
                children: (
                  <div>
                    {(file.done_list?.length || 0) > 0 && (
                      <div style={{ marginBottom: 8 }}>
                        <div style={{ fontSize: '12px', fontWeight: 500, marginBottom: 4, color: '#52c41a' }}>
                          ✓ 已完成步骤:
                        </div>
                        {(file.done_list || []).map((step: string, idx: number) => (
                          <Tag key={idx} color="success" style={{ marginBottom: 4 }}>
                            {step}
                          </Tag>
                        ))}
                      </div>
                    )}
                    {(file.running_list?.length || 0) > 0 && (
                      <div>
                        <div style={{ fontSize: '12px', fontWeight: 500, marginBottom: 4, color: '#1890ff' }}>
                          ↻ 进行中步骤:
                        </div>
                        {(file.running_list || []).map((step: string, idx: number) => (
                          <Tag key={idx} color="processing" style={{ marginBottom: 4 }}>
                            {step}
                          </Tag>
                        ))}
                      </div>
                    )}
                  </div>
                ),
              },
            ]}
          />
        ) : null}
      </div>
    );
  };

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
          <Progress
            percent={progressPct}
            status={
              task.status === 'failed' ? 'exception' : task.status === 'timeout' ? 'exception' : undefined
            }
            strokeColor={getStatusColor(task.status)}
          />

          <div style={{ marginTop: 16 }}>
            {task.files.map((f) => (
              <Card
                key={f.filename}
                size="small"
                style={{ marginBottom: 12, borderLeft: `4px solid ${getStatusColor(f.status)}` }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <div>
                    <strong>{f.filename}</strong>
                    <Tag
                      color={f.status === 'done' ? 'success' : f.status === 'failed' ? 'error' : f.status === 'timeout' ? 'warning' : 'processing'}
                      style={{ marginLeft: 8 }}
                    >
                      {getStatusText(f.status)}
                    </Tag>
                  </div>
                  {f.status === 'done' && (
                    <span style={{ marginLeft: 8, color: '#52c41a', fontSize: '12px' }}>
                      ✓ RAG处理完成
                    </span>
                  )}
                  {f.status === 'uploaded' && (
                    <span style={{ marginLeft: 8, color: '#1890ff', fontSize: '12px' }}>
                      已上传至RAG引擎
                    </span>
                  )}
                </div>

                {f.message && (
                  <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: 8 }}>
                    {f.message}
                  </div>
                )}

                {f.error && (
                  <div style={{ color: 'red', fontSize: '12px', marginBottom: 8 }}>
                    错误: {f.error}
                  </div>
                )}

                {renderStepProgress(f)}
              </Card>
            ))}
          </div>

          {(task.status === 'done' || task.status === 'timeout') && (
            <Button type="primary" onClick={() => navigate('/admin/knowledge')} style={{ marginTop: 16 }}>
              查看知识单元列表
            </Button>
          )}
        </Card>
      )}
    </div>
  );
};
