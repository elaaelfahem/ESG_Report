import { useState, useEffect } from 'react';
import { listPipelineRuns } from '../api/client';
import { RefreshCw, CheckCircle, XCircle, Clock, Loader } from 'lucide-react';

function ActivityPage() {
    const [runs, setRuns] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchRuns = async () => {
        setLoading(true);
        try {
            const res = await listPipelineRuns();
            setRuns(res.runs.reverse());
        } catch (err) {
            console.error('Failed to fetch pipeline runs:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRuns();
    }, []);

    const getStatusIcon = (status) => {
        switch (status) {
            case 'complete':
                return <CheckCircle size={16} style={{ color: 'var(--emerald-400)' }} />;
            case 'error':
                return <XCircle size={16} style={{ color: 'var(--rose-400)' }} />;
            case 'running':
                return <Loader size={16} style={{ color: 'var(--sky-400)', animation: 'spin 1s linear infinite' }} />;
            default:
                return <Clock size={16} style={{ color: 'var(--dark-400)' }} />;
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'complete': return 'badge-success';
            case 'error': return 'badge-error';
            case 'running': return 'badge-info';
            default: return 'badge-warning';
        }
    };

    return (
        <div className="page-container animate-in" style={{ padding: 'var(--space-8)' }}>
            <div className="page-header">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                        <h2>Pipeline Activity</h2>
                        <p>Monitor all pipeline runs and their status</p>
                    </div>
                    <button className="btn btn-secondary" onClick={fetchRuns}>
                        <RefreshCw size={16} />
                        Refresh
                    </button>
                </div>
            </div>

            <div className="card">
                {loading ? (
                    <div style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--dark-400)' }}>
                        <div className="spinner" style={{ margin: '0 auto', width: 24, height: 24 }} />
                    </div>
                ) : runs.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">🔄</div>
                        <div className="empty-state-title">No pipeline runs yet</div>
                        <div className="empty-state-text">
                            Generate a report to see pipeline activity here.
                        </div>
                    </div>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                            <thead>
                                <tr>
                                    <th style={thStyle}>Run ID</th>
                                    <th style={thStyle}>Topic</th>
                                    <th style={thStyle}>Status</th>
                                    <th style={thStyle}>Progress</th>
                                    <th style={thStyle}>Started</th>
                                    <th style={thStyle}>Completed</th>
                                </tr>
                            </thead>
                            <tbody>
                                {runs.map((run) => (
                                    <tr key={run.id} style={{ borderBottom: '1px solid var(--glass-border)' }}>
                                        <td style={tdStyle}>
                                            <code style={{
                                                fontFamily: 'var(--font-mono)',
                                                color: 'var(--sky-400)',
                                                background: 'rgba(14, 165, 233, 0.1)',
                                                padding: '2px 6px',
                                                borderRadius: 'var(--radius-sm)',
                                                fontSize: '0.78rem',
                                            }}>
                                                {run.id}
                                            </code>
                                        </td>
                                        <td style={tdStyle}>{run.topic}</td>
                                        <td style={tdStyle}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                                                {getStatusIcon(run.status)}
                                                <span className={`badge ${getStatusBadge(run.status)}`}>
                                                    {run.status}
                                                </span>
                                            </div>
                                        </td>
                                        <td style={tdStyle}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                                                <div className="progress-bar-container" style={{ width: 100, height: 4 }}>
                                                    <div className="progress-bar-fill" style={{ width: `${run.progress}%` }} />
                                                </div>
                                                <span style={{ fontSize: '0.75rem', color: 'var(--dark-400)' }}>
                                                    {run.progress}%
                                                </span>
                                            </div>
                                        </td>
                                        <td style={{ ...tdStyle, fontSize: '0.75rem', color: 'var(--dark-400)' }}>
                                            {run.created_at ? new Date(run.created_at).toLocaleString() : '—'}
                                        </td>
                                        <td style={{ ...tdStyle, fontSize: '0.75rem', color: 'var(--dark-400)' }}>
                                            {run.completed_at ? new Date(run.completed_at).toLocaleString() : '—'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}

const thStyle = {
    textAlign: 'left',
    padding: 'var(--space-3) var(--space-4)',
    color: 'var(--dark-400)',
    fontWeight: 600,
    fontSize: '0.75rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    borderBottom: '1px solid var(--glass-border)',
};

const tdStyle = {
    padding: 'var(--space-3) var(--space-4)',
    color: 'var(--dark-200)',
};

export default ActivityPage;
