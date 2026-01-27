import { useEffect, useState } from 'react';
import { Plus } from 'lucide-react';
import { HabitCheckbox, ProgressRing, LoadingState, EmptyState } from '../components';
import { useHabitStore } from '../stores';

export function TodayPage() {
    const { todayEntries, habits, loading, fetchTodayEntries, fetchHabits, toggleHabit, createHabit } = useHabitStore();
    const [showAddModal, setShowAddModal] = useState(false);
    const [newHabit, setNewHabit] = useState({ name: '', category: 'general', is_physical: false, weight: 5 });

    useEffect(() => {
        fetchTodayEntries();
        fetchHabits();
    }, []);

    const today = new Date().toISOString().split('T')[0];

    const handleToggle = (habitId, completed) => {
        toggleHabit(habitId, today, completed);
    };

    const handleAddHabit = async (e) => {
        e.preventDefault();
        const success = await createHabit(newHabit);
        if (success) {
            setShowAddModal(false);
            setNewHabit({ name: '', category: 'general', is_physical: false, weight: 5 });
            fetchTodayEntries();
        }
    };

    if (loading && !todayEntries) return <LoadingState />;

    return (
        <div>
            <div className="flex-between mb-lg">
                <h1>Today's Habits</h1>
                <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                    <Plus size={18} /> Add Habit
                </button>
            </div>

            {todayEntries ? (
                <div className="grid-2">
                    <div>
                        <div className="card mb-lg">
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)' }}>
                                <ProgressRing progress={todayEntries.completion_rate} size={100} />
                                <div>
                                    <h2>{todayEntries.completion_count}/{todayEntries.total_habits}</h2>
                                    <p style={{ color: 'var(--text-secondary)' }}>Habits Completed</p>
                                </div>
                            </div>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                            {todayEntries.habits.map(habit => (
                                <HabitCheckbox
                                    key={habit.habit_id}
                                    habit={habit}
                                    checked={habit.completed}
                                    onToggle={(completed) => handleToggle(habit.habit_id, completed)}
                                    disabled={habit.is_physical && todayEntries.physical_completed && !habit.completed}
                                />
                            ))}
                        </div>
                    </div>

                    <div className="card">
                        <h3 className="card-title mb-md">Quick Stats</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                            <div className="flex-between">
                                <span style={{ color: 'var(--text-secondary)' }}>Physical Activity</span>
                                <span className={todayEntries.physical_completed ? 'badge badge-success' : 'badge badge-warning'}>
                                    {todayEntries.physical_completed ? 'Done' : 'Pending'}
                                </span>
                            </div>
                            <div className="flex-between">
                                <span style={{ color: 'var(--text-secondary)' }}>Date</span>
                                <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</span>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <EmptyState
                    title="No habits yet"
                    message="Create your first habit to get started"
                    action={<button className="btn btn-primary mt-md" onClick={() => setShowAddModal(true)}>Add Habit</button>}
                />
            )}

            {showAddModal && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
                        <h3 className="mb-lg">Add New Habit</h3>
                        <form onSubmit={handleAddHabit}>
                            <div className="mb-md">
                                <input className="input" placeholder="Habit name" value={newHabit.name} onChange={e => setNewHabit({ ...newHabit, name: e.target.value })} required />
                            </div>
                            <div className="mb-md">
                                <select className="input" value={newHabit.category} onChange={e => setNewHabit({ ...newHabit, category: e.target.value })}>
                                    <option value="general">General</option>
                                    <option value="health">Health</option>
                                    <option value="physical">Physical</option>
                                    <option value="mental">Mental</option>
                                    <option value="learning">Learning</option>
                                    <option value="creative">Creative</option>
                                </select>
                            </div>
                            <div className="mb-md">
                                <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                                    <input type="checkbox" checked={newHabit.is_physical} onChange={e => setNewHabit({ ...newHabit, is_physical: e.target.checked })} />
                                    Physical activity (max 1/day)
                                </label>
                            </div>
                            <div className="mb-lg">
                                <label style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Weight (1-10): {newHabit.weight}</label>
                                <input type="range" min="1" max="10" value={newHabit.weight} onChange={e => setNewHabit({ ...newHabit, weight: parseInt(e.target.value) })} style={{ width: '100%' }} />
                            </div>
                            <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
                                <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)} style={{ flex: 1 }}>Cancel</button>
                                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Add</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
