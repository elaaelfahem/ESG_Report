import { Search, Shield, PenTool, CheckCircle, Loader2, AlertCircle, Clock } from 'lucide-react';

const STAGES = [
    {
        key: 'init',
        title: 'Initializing Pipeline',
        description: 'Loading models and vectorstore...',
        icon: Clock,
    },
    {
        key: 'agent_a',
        title: 'Agent A — KPI Extractor',
        description: 'Searching documents and extracting ESG metrics...',
        icon: Search,
    },
    {
        key: 'agent_b',
        title: 'Agent B — Compliance Auditor',
        description: 'Auditing data against GRI/SASB/ESRS frameworks...',
        icon: Shield,
    },
    {
        key: 'agent_c',
        title: 'Agent C — Report Writer',
        description: 'Drafting professional ESG report section...',
        icon: PenTool,
    },
    {
        key: 'save',
        title: 'Saving Report',
        description: 'Saving generated report to database...',
        icon: CheckCircle,
    },
];

function AgentProgress({ currentStage, progress, detail, status }) {
    const getStageStatus = (stageKey) => {
        if (status === 'error') {
            const stageIndex = STAGES.findIndex(s => s.key === stageKey);
            const currentIndex = STAGES.findIndex(s => s.key === currentStage);
            if (stageIndex === currentIndex) return 'error';
            if (stageIndex < currentIndex) return 'complete';
            return 'pending';
        }

        const stageIndex = STAGES.findIndex(s => s.key === stageKey);
        const currentIndex = STAGES.findIndex(s => s.key === currentStage);

        if (stageIndex < currentIndex) return 'complete';
        if (stageIndex === currentIndex) {
            if (progress >= 100) return 'complete';
            return 'running';
        }
        return 'pending';
    };

    const getIndicatorContent = (stageStatus, StageIcon) => {
        switch (stageStatus) {
            case 'complete':
                return <CheckCircle size={20} className="text-emerald-400" />;
            case 'running':
                return <Loader2 size={20} className="animate-spin text-emerald-400" />;
            case 'error':
                return <AlertCircle size={20} className="text-rose-400" />;
            default:
                return <StageIcon size={18} opacity={0.4} />;
        }
    };

    return (
        <div className="pipeline-container animate-in">
            {/* Global Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 'var(--space-6)',
                paddingBottom: 'var(--space-4)',
                borderBottom: '1px solid var(--glass-border)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                    <div className="pulse-dot" />
                    <span style={{ fontWeight: 600, color: 'var(--dark-100)', fontSize: '1rem' }}>Autonomous Pipeline</span>
                </div>
                <div style={{
                    background: 'var(--glass-bg)',
                    padding: 'var(--space-1) var(--space-3)',
                    borderRadius: 'var(--radius-full)',
                    border: '1px solid var(--glass-border)',
                    fontSize: '0.75rem',
                    color: 'var(--emerald-400)',
                    fontWeight: 700,
                    letterSpacing: '0.05em'
                }}>
                    {status === 'running' ? 'EXECUTING AGENTS' : (status ? status.toUpperCase() : 'WAITING...')}
                </div>
            </div>

            {/* Global Progress Bar */}
            <div style={{ marginBottom: 'var(--space-8)' }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--space-2)',
                    fontSize: '0.8rem',
                }}>
                    <span style={{ color: 'var(--dark-300)', fontWeight: 500 }}>Global Completion</span>
                    <span style={{ color: 'var(--emerald-400)', fontWeight: 700 }}>{Math.round(progress)}%</span>
                </div>
                <div className="progress-bar-container" style={{ height: '8px', background: 'var(--dark-800)' }}>
                    <div className="progress-bar-fill" style={{
                        width: `${progress}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, var(--emerald-600), var(--emerald-400))',
                        boxShadow: '0 0 15px rgba(16, 185, 129, 0.3)'
                    }} />
                </div>
            </div>

            {/* Stage Steps */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                {STAGES.map((stage, idx) => {
                    const stageStatus = getStageStatus(stage.key);
                    const StageIcon = stage.icon;
                    const isCurrentStage = stage.key === currentStage;

                    return (
                        <div key={stage.key} className={`pipeline-step ${stageStatus}`} style={{
                            display: 'flex',
                            gap: 'var(--space-4)',
                            padding: 'var(--space-4)',
                            borderRadius: 'var(--radius-lg)',
                            background: isCurrentStage ? 'rgba(255, 255, 255, 0.03)' : 'transparent',
                            border: isCurrentStage ? '1px solid var(--glass-border)' : '1px solid transparent',
                            transition: 'all 0.3s ease',
                            position: 'relative',
                            opacity: stageStatus === 'pending' ? 0.5 : 1
                        }}>
                            {/* Vertical line between steps */}
                            {idx < STAGES.length - 1 && (
                                <div style={{
                                    position: 'absolute',
                                    left: '31px',
                                    top: '50px',
                                    width: '2px',
                                    height: 'calc(100% - 20px)',
                                    background: stageStatus === 'complete' ? 'var(--emerald-500)' : 'var(--dark-700)',
                                    zIndex: 0,
                                    opacity: 0.3
                                }} />
                            )}

                            <div className={`step-indicator ${stageStatus}`} style={{
                                width: '36px',
                                height: '36px',
                                minWidth: '36px',
                                borderRadius: 'var(--radius-full)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                zIndex: 1,
                                background: stageStatus === 'complete' ? 'rgba(16, 185, 129, 0.1)' :
                                    stageStatus === 'running' ? 'rgba(16, 185, 129, 0.05)' : 'var(--dark-800)',
                                color: stageStatus === 'complete' || stageStatus === 'running' ? 'var(--emerald-400)' : 'var(--dark-400)',
                                border: stageStatus === 'running' ? '1px solid var(--emerald-500)' : '1px solid transparent'
                            }}>
                                {getIndicatorContent(stageStatus, StageIcon)}
                            </div>

                            <div className="step-content" style={{ flex: 1 }}>
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    marginBottom: '4px'
                                }}>
                                    <span style={{
                                        fontWeight: 600,
                                        color: isCurrentStage ? 'var(--dark-50)' : 'var(--dark-200)',
                                        fontSize: '0.95rem'
                                    }}>
                                        {stage.title}
                                    </span>
                                    {stageStatus === 'running' && (
                                        <div className="shimmer" style={{
                                            fontSize: '0.65rem',
                                            fontWeight: 800,
                                            color: 'var(--emerald-400)',
                                            letterSpacing: '0.1em'
                                        }}>
                                            PROCESSING...
                                        </div>
                                    )}
                                </div>
                                <div style={{
                                    fontSize: '0.8rem',
                                    color: 'var(--dark-400)',
                                    lineHeight: 1.5
                                }}>
                                    {isCurrentStage && detail ? (
                                        <span style={{ color: 'var(--emerald-300)' }}>{detail}</span>
                                    ) : stage.description}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default AgentProgress;
