import { useEffect } from 'react';
import { KPICard, LoadingState, ErrorBanner } from '../components';
import { useAnalyticsStore } from '../stores';

export function MonthlyPage() {
    const { monthlyData, loading, error, fetchMonthlyAnalytics, clearError } = useAnalyticsStore();

    useEffect(() => { fetchMonthlyAnalytics(); }, []);

    if (loading || !monthlyData) return <LoadingState />;

    const gradeColor = monthlyData.performance_grade?.startsWith('A') ? 'var(--success)'
        : monthlyData.performance_grade.startsWith('B') ? 'var(--accent)'
            : monthlyData.performance_grade.startsWith('C') ? 'var(--warning)' : 'var(--danger)';

    return (
        <div>
            <ErrorBanner message={error} onDismiss={clearError} />
            <h1 className="mb-lg">Monthly Report - {new Date(monthlyData.year, monthlyData.month - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</h1>

            <div className="grid-4 mb-lg">
                <div className="kpi-card" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '4rem', fontWeight: 700, color: gradeColor }}>{monthlyData.performance_grade}</div>
                    <div className="kpi-label">Performance Grade</div>
                </div>
                <KPICard value={`${monthlyData.avg_completion_rate.toFixed(0)}%`} label="Avg Completion" />
                <KPICard value={`${monthlyData.avg_weighted_score.toFixed(0)}%`} label="Avg Weighted Score" />
                <KPICard value={monthlyData.consistency_trend >= 0 ? `+${monthlyData.consistency_trend.toFixed(0)}` : monthlyData.consistency_trend.toFixed(0)} label="Consistency Trend" />
            </div>

            <div className="grid-2">
                <div className="card">
                    <h3 className="card-title mb-md">🏆 Top Performers</h3>
                    {monthlyData.top_habits?.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                            {monthlyData.top_habits.map((h, i) => (
                                <div key={i} className="flex-between" style={{ padding: 'var(--space-sm)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                                    <span>{h.habit_name}</span>
                                    <span className="badge badge-success">{h.completion_rate?.toFixed(0) || 0}%</span>
                                </div>
                            ))}
                        </div>
                    ) : <p style={{ color: 'var(--text-muted)' }}>No data</p>}
                </div>

                <div className="card">
                    <h3 className="card-title mb-md">⚠️ Needs Attention</h3>
                    {monthlyData.struggling_habits?.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                            {monthlyData.struggling_habits.map((h, i) => (
                                <div key={i} className="flex-between" style={{ padding: 'var(--space-sm)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                                    <span>{h.habit_name}</span>
                                    <span className="badge badge-danger">{h.completion_rate?.toFixed(0) || 0}%</span>
                                </div>
                            ))}
                        </div>
                    ) : <p style={{ color: 'var(--text-muted)' }}>All habits on track!</p>}
                </div>
            </div>

            <div className="card mt-lg">
                <h3 className="card-title mb-md">Monthly Insights</h3>
                {monthlyData.score_explanation?.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                        {monthlyData.score_explanation.map((e, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)', padding: 'var(--space-md)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                                <span style={{ fontSize: '1.5rem' }}>{e.icon}</span>
                                <span>{e.message}</span>
                            </div>
                        ))}
                    </div>
                ) : <p style={{ color: 'var(--text-muted)' }}>Complete more weeks for insights</p>}
            </div>
        </div>
    );
}
