import { TrendingUp, TrendingDown } from 'lucide-react';

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

export function HabitCheckbox({ habit, checked, onToggle, disabled }) {
    return (
        <div className={`checkbox-container ${disabled ? 'disabled' : ''}`} onClick={() => !disabled && onToggle(!checked)}>
            <div className={`checkbox ${checked ? 'checked' : ''}`}>
                {checked && <span style={{ color: 'white', fontSize: '14px' }}>✓</span>}
            </div>
            <div>
                <div className="checkbox-label">{habit.habit_name}</div>
                <div className="checkbox-category">{habit.category}</div>
            </div>
            {habit.is_physical && <span className="badge badge-warning">Physical</span>}
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
