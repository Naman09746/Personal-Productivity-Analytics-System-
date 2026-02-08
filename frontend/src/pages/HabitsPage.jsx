import { useEffect, useState } from 'react';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { LoadingState, EmptyState, ErrorBanner, Modal, ConfirmDialog } from '../components';
import { HabitForm } from '../components/HabitForm';
import { useHabitStore } from '../stores';

export function HabitsPage() {
    const {
        habits, loading, error,
        fetchHabits, createHabit, updateHabit, deleteHabit, clearError
    } = useHabitStore();
    const [showAddModal, setShowAddModal] = useState(false);
    const [editHabit, setEditHabit] = useState(null);
    const [deleteHabitTarget, setDeleteHabitTarget] = useState(null);
    const [addLoading, setAddLoading] = useState(false);
    const [editLoading, setEditLoading] = useState(false);
    const [deleteLoading, setDeleteLoading] = useState(false);

    useEffect(() => {
        fetchHabits();
    }, []);

    const handleAddHabit = async (formData) => {
        setAddLoading(true);
        const success = await createHabit(formData);
        setAddLoading(false);
        if (success) setShowAddModal(false);
    };

    const handleEditHabit = async (formData) => {
        if (!editHabit?.id) return;
        setEditLoading(true);
        const success = await updateHabit(editHabit.id, formData);
        setEditLoading(false);
        if (success) setEditHabit(null);
    };

    const handleDeleteHabit = async () => {
        if (!deleteHabitTarget?.id) return;
        setDeleteLoading(true);
        const success = await deleteHabit(deleteHabitTarget.id);
        setDeleteLoading(false);
        if (success) setDeleteHabitTarget(null);
    };

    if (loading && habits.length === 0) return <LoadingState />;

    return (
        <div>
            <ErrorBanner message={error} onDismiss={clearError} />
            <div className="flex-between mb-lg">
                <div>
                    <h1>My Habits</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: 4 }}>
                        Add habits once—they stay until you remove them. Check them off daily on Today.
                    </p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                    <Plus size={18} /> Add Habit
                </button>
            </div>

            {habits.length > 0 ? (
                <div className="card">
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                        {habits.map(habit => (
                            <div
                                key={habit.id}
                                className="habit-row"
                                style={{
                                    display: 'flex', alignItems: 'center', gap: 'var(--space-md)',
                                    padding: 'var(--space-md)',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: 'var(--radius-md)',
                                    marginBottom: 'var(--space-sm)'
                                }}
                            >
                                <div style={{ flex: 1 }}>
                                    <div className="checkbox-label">{habit.name}</div>
                                    <div className="checkbox-category">{habit.category}</div>
                                </div>
                                {habit.is_physical && <span className="badge badge-warning">Physical</span>}
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Weight: {habit.weight}</span>
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => setEditHabit(habit)}
                                    style={{ padding: '6px 10px' }}
                                    aria-label="Edit"
                                >
                                    <Pencil size={16} />
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-danger"
                                    onClick={() => setDeleteHabitTarget(habit)}
                                    style={{ padding: '6px 10px' }}
                                    aria-label="Remove"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                <EmptyState
                    title="No habits yet"
                    message="Add your first habit. It will stay in your list until you remove it."
                    action={<button className="btn btn-primary mt-md" onClick={() => setShowAddModal(true)}>Add Habit</button>}
                />
            )}

            {showAddModal && (
                <Modal title="Add New Habit" onClose={() => !addLoading && setShowAddModal(false)}>
                    <HabitForm onSubmit={handleAddHabit} onCancel={() => setShowAddModal(false)} loading={addLoading} />
                </Modal>
            )}

            {editHabit && (
                <Modal title="Edit Habit" onClose={() => !editLoading && setEditHabit(null)}>
                    <HabitForm
                        habit={{ ...editHabit, habit_name: editHabit.name }}
                        onSubmit={handleEditHabit}
                        onCancel={() => setEditHabit(null)}
                        loading={editLoading}
                    />
                </Modal>
            )}

            {deleteHabitTarget && (
                <Modal onClose={() => !deleteLoading && setDeleteHabitTarget(null)}>
                    <ConfirmDialog
                        message={`Remove "${deleteHabitTarget.name}" from your habits? It will disappear from your list.`}
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
