import { useState, useEffect, useRef } from 'react';
import FileUploader from '../components/FileUploader';
import AgentProgress from '../components/AgentProgress';
import ReportViewer from '../components/ReportViewer';
import { runPipeline, getPipelineStatus, getPipelineResult, createProgressWebSocket } from '../api/client';
import { Rocket, Download } from 'lucide-react';

function Upload() {
    const [filesUploaded, setFilesUploaded] = useState(false);
    const [pipelineRunning, setPipelineRunning] = useState(false);
    const [pipelineComplete, setPipelineComplete] = useState(false);
    const [runId, setRunId] = useState(null);
    const [progress, setProgress] = useState(0);
    const [currentStage, setCurrentStage] = useState('init');
    const [stageDetail, setStageDetail] = useState('');
    const [pipelineStatus, setPipelineStatus] = useState(null);
    const [report, setReport] = useState(null);
    const [error, setError] = useState(null);
    const pollingRef = useRef(null);
    const wsRef = useRef(null);

    // WebSocket for real-time progress
    useEffect(() => {
        if (!pipelineRunning) return;

        try {
            wsRef.current = createProgressWebSocket(
                (data) => {
                    if (data.type === 'progress') {
                        setCurrentStage(data.stage);
                        setProgress(data.progress);
                        setStageDetail(data.detail);
                    }
                },
                (err) => {
                    console.warn('WebSocket error, falling back to polling:', err);
                }
            );
        } catch (e) {
            console.warn('WebSocket not available, using polling');
        }

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [pipelineRunning]);

    // Polling fallback for progress
    useEffect(() => {
        if (!runId || !pipelineRunning) return;

        pollingRef.current = setInterval(async () => {
            try {
                const status = await getPipelineStatus(runId);
                setPipelineStatus(status.status);
                setProgress(status.progress || 0);
                setCurrentStage(status.current_stage || 'init');
                setStageDetail(status.detail || '');

                if (status.status === 'complete') {
                    clearInterval(pollingRef.current);
                    setPipelineRunning(false);
                    setPipelineComplete(true);

                    const result = await getPipelineResult(runId);
                    setReport(result);
                } else if (status.status === 'error') {
                    clearInterval(pollingRef.current);
                    setPipelineRunning(false);
                    setError(status.error || 'Pipeline failed');
                }
            } catch (err) {
                console.error('Polling error:', err);
            }
        }, 2000);

        return () => {
            if (pollingRef.current) {
                clearInterval(pollingRef.current);
            }
        };
    }, [runId, pipelineRunning]);

    const handleGenerate = async () => {
        if (!filesUploaded) {
            setError('Please upload at least one ESG document first.');
            return;
        }

        setError(null);
        setPipelineRunning(true);
        setPipelineComplete(false);
        setReport(null);
        setProgress(0);
        setCurrentStage('init');

        try {
            // Backend will use default KPI_CATEGORIES if questions is None
            const result = await runPipeline("Auto-Generated ESG Report 2024", []);
            setRunId(result.run_id);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to start pipeline');
            setPipelineRunning(false);
        }
    };

    return (
        <div className="page-container animate-in" style={{ padding: 'var(--space-8)' }}>
            <div className="page-header">
                <h2>Upload & Generate</h2>
                <p>Upload ESG documents and generate AI-powered reports</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
                {/* Left Column: Upload & Config */}
                <div>
                    {/* File Upload & Trigger */}
                    <div className="card" style={{ marginBottom: 'var(--space-4)' }}>
                        <div className="card-header">
                            <div className="card-title">📁 1. Upload ESG Documents</div>
                        </div>
                        <FileUploader onUploadComplete={() => setFilesUploaded(true)} />

                        <div style={{ marginTop: 'var(--space-6)', borderTop: '1px solid var(--glass-border)', paddingTop: 'var(--space-6)' }}>
                            <div style={{ marginBottom: 'var(--space-4)' }}>
                                <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--dark-100)', marginBottom: '4px' }}>
                                    2. Automated Extraction
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--dark-400)' }}>
                                    Our AI will automatically identify relevant ESG metrics, audit them against GRI/SASB, and generate your report.
                                </div>
                            </div>

                            <button
                                className="btn btn-primary btn-lg"
                                onClick={handleGenerate}
                                disabled={pipelineRunning || !filesUploaded}
                                style={{ width: '100%' }}
                            >
                                {pipelineRunning ? (
                                    <>
                                        <div className="spinner" />
                                        Analyzing Documents...
                                    </>
                                ) : (
                                    <>
                                        <Rocket size={18} />
                                        Generate Auto-ESG Report
                                    </>
                                )}
                            </button>

                            {error && (
                                <div style={{
                                    marginTop: 'var(--space-3)',
                                    padding: 'var(--space-3) var(--space-4)',
                                    background: 'rgba(244, 63, 94, 0.1)',
                                    borderRadius: 'var(--radius-lg)',
                                    color: 'var(--rose-400)',
                                    fontSize: '0.85rem',
                                }}>
                                    ⚠️ {typeof error === 'object' ? (error.message || JSON.stringify(error)) : String(error)}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Right Column: Progress & Results */}
                <div>
                    {pipelineRunning && (
                        <div className="card animate-in">
                            <div className="card-header">
                                <div className="card-title">🤖 Agent Pipeline</div>
                                <span className="badge badge-info">Running</span>
                            </div>
                            <AgentProgress
                                currentStage={currentStage}
                                progress={progress}
                                detail={stageDetail}
                                status={pipelineStatus}
                            />
                        </div>
                    )}

                    {pipelineComplete && report && (
                        <div className="card animate-in">
                            <div className="card-header">
                                <div className="card-title">✅ Report Generated</div>
                                <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                                    <a
                                        href={`http://localhost:8000/api/reports/${report.report_filename}/download`}
                                        className="btn btn-secondary"
                                        style={{ fontSize: '0.8rem' }}
                                        download
                                    >
                                        <Download size={14} />
                                        Download .md
                                    </a>
                                </div>
                            </div>

                            {/* Stats */}
                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: '1fr 1fr 1fr',
                                gap: 'var(--space-2)',
                                marginBottom: 'var(--space-4)',
                            }}>
                                <div style={{ textAlign: 'center', padding: 'var(--space-3)', background: 'var(--emerald-50)', borderRadius: 'var(--radius-lg)' }}>
                                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--emerald-600)' }}>
                                        {report.kpis_extracted}
                                    </div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--dark-400)' }}>KPIs Extracted</div>
                                </div>
                                <div style={{ textAlign: 'center', padding: 'var(--space-3)', background: 'var(--emerald-50)', borderRadius: 'var(--radius-lg)' }}>
                                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--info)' }}>
                                        {report.kpis_audited}
                                    </div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--dark-400)' }}>KPIs Audited</div>
                                </div>
                                <div style={{ textAlign: 'center', padding: 'var(--space-3)', background: 'var(--emerald-50)', borderRadius: 'var(--radius-lg)' }}>
                                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--emerald-700)' }}>
                                        {report.kpis_requested}
                                    </div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--dark-400)' }}>KPIs Requested</div>
                                </div>
                            </div>

                            <ReportViewer
                                content={report.report_content}
                                filename={report.report_filename}
                            />
                        </div>
                    )}

                    {!pipelineRunning && !pipelineComplete && (
                        <div className="card">
                            <div className="empty-state">
                                <div className="empty-state-icon">🤖</div>
                                <div className="empty-state-text">
                                    Upload your PDFs and click Generate. Our AI agents will automatically extract metrics, audit them, and draft your report.
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Upload;
