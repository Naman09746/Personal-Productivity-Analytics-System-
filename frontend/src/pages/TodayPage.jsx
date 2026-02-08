import { useEffect, useState } from 'react';
import { Plus } from 'lucide-react';
import { ProgressRing, LoadingState, EmptyState, ErrorBanner, HabitRow, Modal, ConfirmDialog } from '../components';
import { HabitForm } from '../components/HabitForm';
import { useHabitStore } from '../stores';

export function TodayPage() {
    const {
        todayEntries, habits, loading, toggleLoadingIds, error,
        fetchTodayEntries, fetchHabits, toggleHabit, createHabit, updateHabit, deleteHabit, clearError
    } = useHabitStore();
    const [showAddModal, setShowAddModal] = useState(false);
    const [editHabit, setEditHabit] = useState(null);
    const [deleteHabitTarget, setDeleteHabitTarget] = useState(null);
    const [addLoading, setAddLoading] = useState(false);
    const [editLoading, setEditLoading] = useState(false);
    const [deleteLoading, setDeleteLoading] = useState(false);

    useEffect(() => {
        fetchTodayEntries();
        fetchHabits();
    }, []);

    const today = new Date().toISOString().split('T')[0];

    const handleToggle = (habitId, completed) => {
        toggleHabit(habitId, today, completed);
    };

    const isToggleLoading = (habitId) => toggleLoadingIds.includes(habitId);

    const handleAddHabit = async (formData) => {
        setAddLoading(true);
        const success = await createHabit(formData);
        setAddLoading(false);
        if (success) {
            setShowAddModal(false);
        }
    };

    const handleEditHabit = async (formData) => {
        if (!editHabit?.habit_id) return;
        setEditLoading(true);
        const success = await updateHabit(editHabit.habit_id, formData);
        setEditLoading(false);
        if (success) {
            setEditHabit(null);
        }
    };

    const handleDeleteHabit = async () => {
        if (!deleteHabitTarget?.habit_id) return;
        setDeleteLoading(true);
        const success = await deleteHabit(deleteHabitTarget.habit_id);
        setDeleteLoading(false);
        if (success) {
            setDeleteHabitTarget(null);
        }
    };

    // Merge habit from todayEntries with full habit from habits list (for edit form)
    const getHabitForEdit = (h) => {
        const full = habits.find(x => x.id === h.habit_id);
        return {
            habit_id: h.habit_id,
            habit_name: h.habit_name,
            name: h.habit_name,
            category: h.category,
            is_physical: h.is_physical,
            weight: full?.weight ?? 5,
            target_per_week: full?.target_per_week ?? 7,
            goal_threshold: full?.goal_threshold ?? 80
        };
    };

    if (loading && !todayEntries) return <LoadingState />;

    return (
        <div>
            <ErrorBanner message={error} onDismiss={clearError} />
            <div className="flex-between mb-lg">
                <div>
                    <h1>Today's Habits</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: 4 }}>
                        Habits stay until you remove them. Just check off daily.
                    </p>
                </div>
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
                                <HabitRow
                                    key={habit.habit_id}
                                    habit={habit}
                                    checked={habit.completed}
                                    onToggle={(completed) => handleToggle(habit.habit_id, completed)}
                                    disabled={(habit.is_physical && todayEntries.physical_completed && !habit.completed) || isToggleLoading(habit.habit_id)}
                                    isLoading={isToggleLoading(habit.habit_id)}
                                    onEdit={() => setEditHabit(getHabitForEdit(habit))}
                                    onDelete={() => setDeleteHabitTarget(habit)}
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
                    message="Add your first habit once and it will appear here every day until you remove it."
                    action={<button className="btn btn-primary mt-md" onClick={() => setShowAddModal(true)}>Add Habit</button>}
                />
            )}

            {showAddModal && (
                <Modal title="Add New Habit" onClose={() => !addLoading && setShowAddModal(false)}>
                    <HabitForm
                        onSubmit={handleAddHabit}
                        onCancel={() => setShowAddModal(false)}
                        loading={addLoading}
                    />
                </Modal>
            )}

            {editHabit && (
                <Modal title="Edit Habit" onClose={() => !editLoading && setEditHabit(null)}>
                    <HabitForm
                        habit={editHabit}
                        onSubmit={handleEditHabit}
                        onCancel={() => setEditHabit(null)}
                        loading={editLoading}
                    />
                </Modal>
            )}

            {deleteHabitTarget && (
                <Modal onClose={() => !deleteLoading && setDeleteHabitTarget(null)}>
                    <ConfirmDialog
                        message={`Remove "${deleteHabitTarget.habit_name}" from your habits? It will disappear from your list.`}
                        confirmLabel="Remove"
                        onConfirm={handleDeleteHabit}
                        onCancel={() => setDeleteHabitTarget(null)}
                        loading={deleteLoading}
                    />
                </Modal>
            )}
        </div>
    );
}
