import { useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { KPICard, LoadingState } from '../components';
import { WeeklyChart } from '../components/Charts';
import { useAnalyticsStore } from '../stores';

export function WeeklyPage() {
    const { weeklyData, loading, fetchWeeklyAnalytics } = useAnalyticsStore();

    useEffect(() => { fetchWeeklyAnalytics(); }, []);

    if (loading || !weeklyData) return <LoadingState />;

    return (
        <div>
            <div className="flex-between mb-lg">
                <h1>Weekly Analytics</h1>
                <div className="flex gap-sm">
                    <button className="btn btn-secondary"><ChevronLeft size={18} /></button>
                    <span style={{ padding: '8px 16px' }}>{weeklyData.week_start} - {weeklyData.week_end}</span>
                    <button className="btn btn-secondary"><ChevronRight size={18} /></button>
                </div>
            </div>

            <div className="grid-3 mb-lg">
                <KPICard value={`${weeklyData.completion_rate.toFixed(0)}%`} label="Completion Rate" trend={weeklyData.comparison_to_last_week} trendLabel="vs last week" />
                <KPICard value={`${weeklyData.weighted_score.toFixed(0)}%`} label="Weighted Score" />
                <KPICard value={`${weeklyData.consistency_score.toFixed(0)}%`} label="Consistency" />
            </div>

            <div className="grid-2">
                <div className="card">
                    <h3 className="card-title mb-md">Daily Performance</h3>
                    <WeeklyChart dailyRates={weeklyData.daily_rates} />
                </div>

                <div className="card">
                    <h3 className="card-title mb-md">Insights</h3>
                    {weeklyData.insights?.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                            {weeklyData.insights.map((insight, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)', padding: 'var(--space-sm)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                                    <span style={{ fontSize: '1.5rem' }}>{insight.icon}</span>
                                    <span>{insight.message}</span>
                                </div>
                            ))}
                        </div>
                    ) : <p style={{ color: 'var(--text-muted)' }}>No insights yet</p>}
                </div>
            </div>

            <div className="card mt-lg">
                <h3 className="card-title mb-md">Habit Breakdown</h3>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)' }}>
                                <th style={{ textAlign: 'left', padding: 'var(--space-sm)', color: 'var(--text-secondary)' }}>Habit</th>
                                <th style={{ textAlign: 'center', padding: 'var(--space-sm)', color: 'var(--text-secondary)' }}>Completed</th>
                                <th style={{ textAlign: 'center', padding: 'var(--space-sm)', color: 'var(--text-secondary)' }}>Rate</th>
                                <th style={{ textAlign: 'center', padding: 'var(--space-sm)', color: 'var(--text-secondary)' }}>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {weeklyData.habit_breakdown?.map(h => (
                                <tr key={h.habit_id} style={{ borderBottom: '1px solid var(--border)' }}>
                                    <td style={{ padding: 'var(--space-sm)' }}>{h.habit_name}</td>
                                    <td style={{ textAlign: 'center', padding: 'var(--space-sm)' }}>{h.completed_count}/{h.target_count}</td>
                                    <td style={{ textAlign: 'center', padding: 'var(--space-sm)' }}>{h.completion_rate.toFixed(0)}%</td>
                                    <td style={{ textAlign: 'center', padding: 'var(--space-sm)' }}>
                                        <span className={`badge ${h.is_below_threshold ? 'badge-danger' : 'badge-success'}`}>
                                            {h.is_below_threshold ? 'Below Goal' : 'On Track'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
