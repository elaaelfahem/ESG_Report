import { NavLink } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

function Dashboard() {
    return (
        <div className="page-container animate-in" style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 'calc(100vh - 120px)',
            padding: 'var(--space-8)'
        }}>
            <div style={{
                display: 'flex',
                background: 'white',
                borderRadius: 'var(--radius-2xl)',
                boxShadow: 'var(--shadow-xl)',
                overflow: 'hidden',
                maxWidth: '1100px',
                width: '100%',
                margin: '0 auto',
                flexDirection: 'row'
            }}>

                {/* Left Side: Graphic */}
                <div style={{
                    flex: '1',
                    background: '#f8fafc', // Subtle light tone for graphic container
                    position: 'relative',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: 'var(--space-8)'
                }}>
                    <img
                        src="/assets/dashboard_hero.png"
                        alt="ESG Strategy AI Dashboard Graphic"
                        style={{
                            maxWidth: '100%',
                            height: 'auto',
                            objectFit: 'contain'
                        }}
                    />
                </div>

                {/* Right Side: Content */}
                <div style={{
                    flex: '1.1',
                    padding: 'var(--space-12) var(--space-10)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    background: 'white'
                }}>
                    <h1 style={{
                        fontSize: '2.8rem',
                        fontWeight: 800,
                        color: 'var(--dark-50)',
                        lineHeight: 1.15,
                        marginBottom: 'var(--space-4)',
                        fontFamily: 'var(--font-display)',
                        letterSpacing: '-0.02em'
                    }}>
                        ESG Strategy<br />Reporting AI
                    </h1>

                    <p style={{
                        color: 'var(--dark-300)',
                        fontSize: '1.05rem',
                        lineHeight: 1.6,
                        marginBottom: 'var(--space-8)',
                        fontFamily: 'var(--font-sans)',
                        maxWidth: '90%'
                    }}>
                        Upload your sustainability PDFs and let our multi-agent AI pipeline extract KPIs, audit compliance data against GRI/SASB standards, and generate beautifully formatted Markdown CSRD reports in seconds.
                    </p>

                    <div style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: 'var(--dark-400)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        marginBottom: 'var(--space-3)'
                    }}>
                        Powered by Multi-Agent RAG
                    </div>

                    <div>
                        <NavLink
                            to="/upload"
                            className="btn btn-primary"
                            style={{
                                padding: 'var(--space-3) var(--space-8)',
                                fontSize: '0.9rem'
                            }}
                        >
                            START GENERATING <ArrowRight size={18} />
                        </NavLink>
                    </div>
                </div>

            </div>
        </div>
    );
}

export default Dashboard;
