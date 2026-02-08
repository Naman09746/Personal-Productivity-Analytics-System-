import { useState, useRef, useEffect } from 'react';
import { TrendingUp, TrendingDown, MoreVertical, Pencil, Trash2 } from 'lucide-react';

export function KPICard({ value, label, trend, trendLabel, icon: Icon }) {
    const isPositive = trend > 0;

    return (
        <div className="kpi-card">
            <div className="flex-between">
                <div>
                    <div className="kpi-value">{value}</div>
                    <div className="kpi-label">{label}</div>
                </div>
                {Icon && <Icon size={32} style={{ color: 'var(--accent)', opacity: 0.5 }} />}
            </div>
            {trend !== undefined && (
                <div className={`kpi-trend ${isPositive ? 'positive' : 'negative'}`}>
                    {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                    <span>{isPositive ? '+' : ''}{trend}% {trendLabel}</span>
                </div>
            )}
        </div>
    );
}

export function ProgressRing({ progress, size = 120, strokeWidth = 8 }) {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (progress / 100) * circumference;

    return (
        <div className="progress-ring" style={{ width: size, height: size }}>
            <svg width={size} height={size}>
                <circle className="progress-ring-bg" cx={size / 2} cy={size / 2} r={radius} strokeWidth={strokeWidth} fill="none" />
                <circle className="progress-ring-progress" cx={size / 2} cy={size / 2} r={radius} strokeWidth={strokeWidth} fill="none"
                    strokeDasharray={circumference} strokeDashoffset={offset} />
            </svg>
            <span className="progress-ring-text">{Math.round(progress)}%</span>
        </div>
    );
}

export function HabitCheckbox({ habit, checked, onToggle, disabled, isLoading }) {
    return (
        <div className={`checkbox-container ${disabled ? 'disabled' : ''} ${isLoading ? 'loading' : ''}`} onClick={() => !disabled && onToggle(!checked)}>
            <div className={`checkbox ${checked ? 'checked' : ''}`}>
                {isLoading ? <span className="loading-spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> : checked && <span style={{ color: 'white', fontSize: '14px' }}>✓</span>}
            </div>
            <div>
                <div className="checkbox-label">{habit.habit_name}</div>
                <div className="checkbox-category">{habit.category}</div>
            </div>
            {habit.is_physical && <span className="badge badge-warning">Physical</span>}
        </div>
    );
}

/** Habit row with checkbox + Edit/Delete actions */
export function HabitRow({ habit, checked, onToggle, disabled, isLoading, onEdit, onDelete }) {
    const [menuOpen, setMenuOpen] = useState(false);
    const menuRef = useRef(null);

    useEffect(() => {
        const close = (e) => {
            if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
        };
        document.addEventListener('click', close);
        return () => document.removeEventListener('click', close);
    }, []);

    return (
        <div className="habit-row" style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-md)',
            padding: 'var(--space-md)',
            background: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--space-sm)'
        }}>
            <div
                className={`checkbox ${checked ? 'checked' : ''}`}
                style={{ flexShrink: 0, cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.6 : 1 }}
                onClick={() => !disabled && onToggle(!checked)}
            >
                {isLoading ? <span className="loading-spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> : checked && <span style={{ color: 'white', fontSize: '14px' }}>✓</span>}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
                <div className="checkbox-label">{habit.habit_name}</div>
                <div className="checkbox-category">{habit.category}</div>
            </div>
            {habit.is_physical && <span className="badge badge-warning">Physical</span>}
            <div style={{ position: 'relative' }} ref={menuRef}>
                <button
                    type="button"
                    className="btn btn-icon"
                    onClick={(e) => { e.stopPropagation(); setMenuOpen(v => !v); }}
                    aria-label="Habit options"
                    style={{ padding: 4, background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
                >
                    <MoreVertical size={18} />
                </button>
                {menuOpen && (
                    <div className="dropdown-menu" style={{
                        position: 'absolute', right: 0, top: '100%', marginTop: 4,
                        background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
                        boxShadow: 'var(--shadow-lg)', minWidth: 120, zIndex: 50
                    }}>
                        <button type="button" onClick={() => { setMenuOpen(false); onEdit?.(); }} style={{
                            display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '10px 12px',
                            background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', textAlign: 'left', fontSize: '0.9rem'
                        }}>
                            <Pencil size={16} /> Edit
                        </button>
                        <button type="button" onClick={() => { setMenuOpen(false); onDelete?.(); }} style={{
                            display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '10px 12px',
                            background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', textAlign: 'left', fontSize: '0.9rem'
                        }}>
                            <Trash2 size={16} /> Remove
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

/** Modal backdrop + container */
export function Modal({ title, onClose, children }) {
    return (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}
            onClick={(e) => e.target === e.currentTarget && onClose?.()}
        >
            <div className="card" style={{ width: '100%', maxWidth: 400 }} onClick={e => e.stopPropagation()}>
                {title && <h3 className="mb-lg">{title}</h3>}
                {children}
            </div>
        </div>
    );
}

/** Confirmation dialog */
export function ConfirmDialog({ message, confirmLabel = 'Remove', onConfirm, onCancel, loading }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <p style={{ color: 'var(--text-secondary)' }}>{message}</p>
            <div style={{ display: 'flex', gap: 'var(--space-sm)', justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={loading}>Cancel</button>
                <button type="button" className="btn btn-danger" onClick={onConfirm} disabled={loading}>
                    {loading ? '…' : confirmLabel}
                </button>
            </div>
        </div>
    );
}

export function LoadingState() {
    return (
        <div className="empty-state">
            <div className="loading-spinner" style={{ margin: '0 auto' }}></div>
            <p className="mt-md">Loading...</p>
        </div>
    );
}

export function EmptyState({ title, message, action }) {
    return (
        <div className="empty-state">
            <h3>{title}</h3>
            <p>{message}</p>
            {action}
        </div>
    );
}

export function ErrorState({ message, onRetry }) {
    return (
        <div className="error-state">
            <p>{message}</p>
            {onRetry && <button className="btn btn-secondary mt-md" onClick={onRetry}>Retry</button>}
        </div>
    );
}

export function ErrorBanner({ message, onDismiss }) {
    if (!message) return null;
    return (
        <div className="error-banner" role="alert" style={{
            padding: 'var(--space-md) var(--space-lg)',
            background: 'var(--danger)',
            color: 'white',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--space-lg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--space-md)'
        }}>
            <span>{message}</span>
            {onDismiss && (
                <button type="button" onClick={onDismiss} aria-label="Dismiss" style={{
                    background: 'transparent', border: 'none', color: 'white', cursor: 'pointer',
                    padding: 4, fontSize: '1.25rem', lineHeight: 1
                }}>×</button>
            )}
        </div>
    );
}
