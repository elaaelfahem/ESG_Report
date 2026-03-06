import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, FileText, Activity } from 'lucide-react';

function Header() {
    return (
        <header className="header">
            <div className="header-logo">
                <div className="header-logo-icon">🌱</div>
                <div className="header-logo-text">
                    <h1>ESG Suite</h1>
                    <span>Multi-Agent AI</span>
                </div>
            </div>

            <nav className="header-nav">
                <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} end>
                    <LayoutDashboard className="icon" size={18} />
                    Dashboard
                </NavLink>
                <NavLink to="/upload" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    <Upload className="icon" size={18} />
                    Upload & Generate
                </NavLink>
                <NavLink to="/reports" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    <FileText className="icon" size={18} />
                    Reports
                </NavLink>
                <div className="nav-divider"></div>
                <NavLink to="/activity" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                    <Activity className="icon" size={18} />
                    Pipeline Activity
                </NavLink>
            </nav>

            <div className="header-status">
                <div className="status-dot"></div>
                <span>Ollama Connected</span>
            </div>
        </header>
    );
}

export default Header;
