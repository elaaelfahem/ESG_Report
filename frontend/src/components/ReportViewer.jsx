import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function ReportViewer({ content, filename }) {
    if (!content) {
        return (
            <div className="empty-state">
                <div className="empty-state-icon">📄</div>
                <div className="empty-state-title">No Report Selected</div>
                <div className="empty-state-text">
                    Generate a new report or select an existing one to view it here.
                </div>
            </div>
        );
    }

    return (
        <div>
            {filename && (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--space-4)',
                    paddingBottom: 'var(--space-4)',
                    borderBottom: '1px solid var(--glass-border)',
                }}>
                    <div>
                        <h3 style={{
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            color: 'var(--dark-100)',
                            marginBottom: 'var(--space-1)',
                        }}>
                            {filename}
                        </h3>
                        <span className="badge badge-success">Generated Report</span>
                    </div>
                </div>
            )}
            <div className="report-viewer">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {content}
                </ReactMarkdown>
            </div>
        </div>
    );
}

export default ReportViewer;
