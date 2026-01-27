import { useEffect } from 'react';
import { Target, Flame, CheckCircle, TrendingUp } from 'lucide-react';
import { KPICard, ProgressRing, LoadingState } from '../components';
import { TrendChart } from '../components/Charts';
import { useAnalyticsStore, useHabitStore } from '../stores';

export function DashboardPage() {
    const { todayStats, trends, fetchTodayStats, fetchTrends } = useAnalyticsStore();
    const { todayEntries, fetchTodayEntries } = useHabitStore();

    useEffect(() => {
        fetchTodayStats();
        fetchTodayEntries();
        fetchTrends('weekly');
    }, []);

    if (!todayStats) return <LoadingState />;

    return (
        <div>
            <h1 className="mb-lg">Dashboard</h1>

            <div className="grid-4 mb-lg">
                <KPICard value={`${todayStats.completion_rate.toFixed(0)}%`} label="Today's Progress" icon={Target} />
                <KPICard value={todayStats.streak_days} label="Day Streak" icon={Flame} />
                <KPICard value={`${todayStats.completed}/${todayStats.total}`} label="Habits Complete" icon={CheckCircle} />
                <KPICard value={todayStats.physical_done ? '✓' : '—'} label="Physical Activity" icon={TrendingUp} />
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Today's Progress</h3>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--space-lg)' }}>
                        <ProgressRing progress={todayStats.completion_rate} size={160} />
                    </div>
                    {todayEntries && (
                        <div className="mt-md">
                            <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
                                {todayEntries.completion_count} of {todayEntries.total_habits} habits completed
                            </p>
                        </div>
                    )}
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Weekly Trend</h3>
                    </div>
                    <TrendChart trends={trends} />
                </div>
            </div>
        </div>
    );
}
