import { useState, useEffect } from 'react';
import { api } from '../api/client';
import './JobsPanel.css';

interface Job {
  id: number;
  title: string;
  description: string;
  job_type: string;
  required_job_class: string;
  base_pay: number;
  max_workers: number;
  current_workers: number;
  location_id: number;
}

interface WorkSession {
  work_session_id: number;
  job_id: number;
  started_at: string;
  duration_minutes: number;
}

export default function JobsPanel() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [currentWork, setCurrentWork] = useState<WorkSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadJobs();
    loadCurrentWork();
  }, []);

  const loadJobs = async () => {
    try {
      const { data } = await api.getAvailableJobs();
      setJobs(data);
    } catch (error) {
      console.error('加载工作失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentWork = async () => {
    try {
      const { data } = await api.getCurrentWork();
      if (data.active) {
        setCurrentWork(data.work_session);
      }
    } catch (error) {
      console.error('加载当前工作失败:', error);
    }
  };

  const handleStartWork = async (jobId: number) => {
    try {
      const { data } = await api.startWork({ job_id: jobId });
      setCurrentWork(data);
      alert('开始工作！');
      loadJobs();
    } catch (error: any) {
      alert(error.response?.data?.detail || '开始工作失败');
    }
  };

  const handleEndWork = async () => {
    if (!currentWork) return;

    try {
      const { data } = await api.endWork({ work_session_id: currentWork.work_session_id });
      alert(`工作完成！获得 ${data.earnings.toFixed(0)} 金币`);
      setCurrentWork(null);
      loadJobs();
    } catch (error: any) {
      alert(error.response?.data?.detail || '结束工作失败');
    }
  };

  if (loading) {
    return <div className="jobs-panel loading">加载中...</div>;
  }

  return (
    <div className="jobs-panel">
      {currentWork && (
        <div className="current-work-card">
          <div className="work-header">
            <h3>🔨 工作中</h3>
            <button onClick={handleEndWork} className="end-work-btn">
              结束工作
            </button>
          </div>
          <div className="work-info">
            <p>已工作: {currentWork.duration_minutes} 分钟</p>
          </div>
        </div>
      )}

      <div className="jobs-header">
        <h2>💼 可用工作</h2>
        <span className="jobs-count">{jobs.length} 个工作</span>
      </div>

      <div className="jobs-list">
        {jobs.map(job => (
          <div key={job.id} className="job-card">
            <div className="job-header">
              <h3>{job.title}</h3>
              <span className="job-pay">💰 {job.base_pay}/小时</span>
            </div>
            <p className="job-description">{job.description}</p>
            <div className="job-footer">
              <div className="job-meta">
                <span className="job-type">{job.job_type}</span>
                <span className="job-workers">
                  👥 {job.current_workers}/{job.max_workers}
                </span>
              </div>
              <button
                onClick={() => handleStartWork(job.id)}
                disabled={!!currentWork || job.current_workers >= job.max_workers}
                className="start-work-btn"
              >
                {currentWork ? '工作中' : '开始工作'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
