function KPICard({ metric, value, unit, year, confidence, source }) {
    const getConfidenceColor = (conf) => {
        if (!conf) return 'var(--dark-400)';
        if (conf === 'high' || conf > 0.7) return 'var(--emerald-400)';
        if (conf === 'medium' || conf > 0.4) return 'var(--amber-400)';
        return 'var(--rose-400)';
    };

    const getConfidenceBadge = (conf) => {
        if (!conf) return 'badge-info';
        if (conf === 'high' || conf > 0.7) return 'badge-success';
        if (conf === 'medium' || conf > 0.4) return 'badge-warning';
        return 'badge-error';
    };

    return (
        <div className="card" style={{ padding: 'var(--space-4) var(--space-5)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <div style={{
                        fontSize: '0.75rem',
                        color: 'var(--dark-400)',
                        fontWeight: 500,
                        marginBottom: 'var(--space-1)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                    }}>
                        {metric || 'Unknown Metric'}
                    </div>
                    <div style={{
                        fontSize: '1.5rem',
                        fontWeight: 700,
                        color: 'var(--dark-50)',
                        lineHeight: 1,
                    }}>
                        {value || 'N/A'}
                        {unit && (
                            <span style={{
                                fontSize: '0.8rem',
                                color: 'var(--dark-400)',
                                fontWeight: 400,
                                marginLeft: 'var(--space-1)'
                            }}>
                                {unit}
                            </span>
                        )}
                    </div>
                </div>
                {confidence && (
                    <span className={`badge ${getConfidenceBadge(confidence)}`}>
                        {typeof confidence === 'string' ? confidence : `${Math.round(confidence * 100)}%`}
                    </span>
                )}
            </div>
            <div style={{
                display: 'flex',
                gap: 'var(--space-4)',
                marginTop: 'var(--space-3)',
                fontSize: '0.75rem',
                color: 'var(--dark-500)',
            }}>
                {year && <span>📅 {year}</span>}
                {source && <span>📁 {source}</span>}
            </div>
        </div>
    );
}

export default KPICard;
