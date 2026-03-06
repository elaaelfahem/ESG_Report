import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { listReports, getReport, deleteReport, downloadReportUrl } from '../api/client';
import ReportViewer from '../components/ReportViewer';
import { Download, Trash2, FileText, RefreshCw } from 'lucide-react';

function Reports() {
    const [searchParams] = useSearchParams();
    const [reports, setReports] = useState([]);
    const [selectedReport, setSelectedReport] = useState(null);
    const [reportContent, setReportContent] = useState(null);
    const [loading, setLoading] = useState(true);
    const [loadingContent, setLoadingContent] = useState(false);

    const fetchReports = async () => {
        setLoading(true);
        try {
            const res = await listReports();
            setReports(res.reports);

            // Auto-select from URL param
            const fileParam = searchParams.get('file');
            if (fileParam && res.reports.some(r => r.filename === fileParam)) {
                loadReport(fileParam);
            }
        } catch (err) {
            console.error('Failed to fetch reports:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchReports();
    }, []);

    const loadReport = async (filename) => {
        setSelectedReport(filename);
        setLoadingContent(true);
        try {
            const res = await getReport(filename);
            setReportContent(res.content);
        } catch (err) {
            console.error('Failed to load report:', err);
        } finally {
            setLoadingContent(false);
        }
    };

    const handleDelete = async (filename) => {
        if (!confirm(`Delete ${filename}?`)) return;
        try {
            await deleteReport(filename);
            setReports(prev => prev.filter(r => r.filename !== filename));
            if (selectedReport === filename) {
                setSelectedReport(null);
                setReportContent(null);
            }
        } catch (err) {
            console.error('Failed to delete report:', err);
        }
    };

    return (
        <div className="page-container animate-in" style={{ padding: 'var(--space-8)' }}>
            <div className="page-header">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                        <h2>Reports</h2>
                        <p>View and manage your generated ESG reports</p>
                    </div>
                    <button className="btn btn-secondary" onClick={fetchReports}>
                        <RefreshCw size={16} />
                        Refresh
                    </button>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: 'var(--space-6)', minHeight: '60vh' }}>
                {/* Report List */}
                <div className="card" style={{ alignSelf: 'start' }}>
                    <div className="card-header">
                        <div className="card-title">📄 All Reports</div>
                        <span className="badge badge-info">{reports.length}</span>
                    </div>

                    {loading ? (
                        <div style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--dark-400)' }}>
                            <div className="spinner" style={{ margin: '0 auto', width: 24, height: 24 }} />
                        </div>
                    ) : reports.length === 0 ? (
                        <div className="empty-state" style={{ padding: 'var(--space-8)' }}>
                            <div style={{ fontSize: '2rem', marginBottom: 'var(--space-2)' }}>📝</div>
                            <div className="empty-state-title">No reports</div>
                            <div className="empty-state-text">Generate your first report to see it here</div>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                            {reports.map((report) => (
                                <div
                                    key={report.filename}
                                    onClick={() => loadReport(report.filename)}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        padding: 'var(--space-3) var(--space-4)',
                                        borderRadius: 'var(--radius-lg)',
                                        cursor: 'pointer',
                                        transition: 'all 150ms',
                                        background: selectedReport === report.filename
                                            ? 'var(--emerald-50)'
                                            : 'var(--dark-800)',
                                        border: selectedReport === report.filename
                                            ? '1px solid var(--emerald-200)'
                                            : '1px solid transparent',
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', overflow: 'hidden' }}>
                                        <FileText size={16} style={{ color: 'var(--emerald-400)', flexShrink: 0 }} />
                                        <div style={{ overflow: 'hidden' }}>
                                            <div style={{
                                                fontSize: '0.8rem',
                                                fontWeight: 500,
                                                color: 'var(--dark-200)',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis',
                                                whiteSpace: 'nowrap',
                                            }}>
                                                {report.filename}
                                            </div>
                                            <div style={{ fontSize: '0.7rem', color: 'var(--dark-500)' }}>
                                                {(report.size_bytes / 1024).toFixed(1)} KB
                                            </div>
                                        </div>
                                    </div>

                                    <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                                        {report.pdf_filename && (
                                            <a
                                                href={downloadReportUrl(report.pdf_filename)}
                                                onClick={(e) => e.stopPropagation()}
                                                className="btn btn-icon btn-primary"
                                                title="Download PDF"
                                                download
                                                style={{ padding: '0.4rem 0.6rem', fontSize: '0.8rem', gap: '4px' }}
                                            >
                                                <Download size={12} /> PDF
                                            </a>
                                        )}
                                        <a
                                            href={downloadReportUrl(report.md_filename || report.filename)}
                                            onClick={(e) => e.stopPropagation()}
                                            className="btn btn-icon btn-secondary"
                                            title="Download Markdown"
                                            download
                                        >
                                            <Download size={12} />
                                        </a>
                                        <button
                                            className="btn btn-icon btn-danger"
                                            onClick={(e) => { e.stopPropagation(); handleDelete(report.filename); }}
                                            title="Delete"
                                        >
                                            <Trash2 size={12} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Report Content */}
                <div className="card">
                    {loadingContent ? (
                        <div style={{ textAlign: 'center', padding: 'var(--space-16)', color: 'var(--dark-400)' }}>
                            <div className="spinner" style={{ margin: '0 auto var(--space-4)', width: 32, height: 32 }} />
                            <div>Loading report...</div>
                        </div>
                    ) : (
                        <ReportViewer content={reportContent} filename={selectedReport} />
                    )}
                </div>
            </div>
        </div>
    );
}

export default Reports;
