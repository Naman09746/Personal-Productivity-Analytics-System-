import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores';

export function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login, loading, error, clearError } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const success = await login(email, password);
        if (success) navigate('/');
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
                <h1 style={{ textAlign: 'center', marginBottom: 'var(--space-lg)' }}>PPAS</h1>
                <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: 'var(--space-xl)' }}>
                    Personal Productivity Analytics
                </p>

                {error && <div className="error-state mb-md" onClick={clearError}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="mb-md">
                        <input type="email" className="input" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
                    </div>
                    <div className="mb-md">
                        <input type="password" className="input" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
                    </div>
                    <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: 'var(--space-lg)', color: 'var(--text-secondary)' }}>
                    Don't have an account? <Link to="/register" style={{ color: 'var(--accent)' }}>Register</Link>
                </p>
            </div>
        </div>
    );
}

export function RegisterPage() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { register, loading, error, clearError } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const success = await register(email, password, name);
        if (success) navigate('/');
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
                <h1 style={{ textAlign: 'center', marginBottom: 'var(--space-lg)' }}>Create Account</h1>

                {error && <div className="error-state mb-md" onClick={clearError}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="mb-md">
                        <input type="text" className="input" placeholder="Name" value={name} onChange={e => setName(e.target.value)} required />
                    </div>
                    <div className="mb-md">
                        <input type="email" className="input" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
                    </div>
                    <div className="mb-md">
                        <input type="password" className="input" placeholder="Password (min 8 chars)" value={password} onChange={e => setPassword(e.target.value)} minLength={8} required />
                    </div>
                    <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
                        {loading ? 'Creating...' : 'Create Account'}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: 'var(--space-lg)', color: 'var(--text-secondary)' }}>
                    Already have an account? <Link to="/login" style={{ color: 'var(--accent)' }}>Sign In</Link>
                </p>
            </div>
        </div>
    );
}
