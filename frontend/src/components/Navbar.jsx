import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, CheckSquare, List, BarChart3, Calendar, LogOut } from 'lucide-react';
import { useAuthStore } from '../stores';

export function Navbar() {
    const location = useLocation();
    const navigate = useNavigate();
    const logout = useAuthStore(s => s.logout);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const links = [
        { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/today', icon: CheckSquare, label: 'Today' },
        { to: '/habits', icon: List, label: 'Habits' },
        { to: '/weekly', icon: BarChart3, label: 'Weekly' },
        { to: '/monthly', icon: Calendar, label: 'Monthly' },
    ];

    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">PPAS</Link>
            <ul className="navbar-nav">
                {links.map(({ to, icon: Icon, label }) => (
                    <li key={to}>
                        <Link to={to} className={`nav-link ${location.pathname === to ? 'active' : ''}`}>
                            <Icon size={18} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                            {label}
                        </Link>
                    </li>
                ))}
                <li>
                    <button onClick={handleLogout} className="nav-link" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                        <LogOut size={18} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                        Logout
                    </button>
                </li>
            </ul>
        </nav>
    );
}
