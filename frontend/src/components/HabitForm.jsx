import { useState } from 'react';

const CATEGORIES = [
    { value: 'general', label: 'General' },
    { value: 'health', label: 'Health' },
    { value: 'physical', label: 'Physical' },
    { value: 'mental', label: 'Mental' },
    { value: 'learning', label: 'Learning' },
    { value: 'creative', label: 'Creative' }
];

export function HabitForm({ habit, onSubmit, onCancel, loading }) {
    const [form, setForm] = useState(habit ? {
        name: habit.habit_name || habit.name,
        category: habit.category || 'general',
        is_physical: habit.is_physical || false,
        weight: habit.weight ?? 5,
        target_per_week: habit.target_per_week ?? 7,
        goal_threshold: habit.goal_threshold ?? 80
    } : {
        name: '',
        category: 'general',
        is_physical: false,
        weight: 5,
        target_per_week: 7,
        goal_threshold: 80
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(form);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="mb-md">
                <input
                    className="input"
                    placeholder="Habit name"
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    required
                />
            </div>
            <div className="mb-md">
                <select
                    className="input"
                    value={form.category}
                    onChange={e => setForm({ ...form, category: e.target.value })}
                >
                    {CATEGORIES.map(c => (
                        <option key={c.value} value={c.value}>{c.label}</option>
                    ))}
                </select>
            </div>
            <div className="mb-md">
                <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <input
                        type="checkbox"
                        checked={form.is_physical}
                        onChange={e => setForm({ ...form, is_physical: e.target.checked })}
                    />
                    Physical activity (max 1/day)
                </label>
            </div>
            <div className="mb-lg">
                <label style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Weight (1-10): {form.weight}</label>
                <input
                    type="range"
                    min="1"
                    max="10"
                    value={form.weight}
                    onChange={e => setForm({ ...form, weight: parseInt(e.target.value) })}
                    style={{ width: '100%' }}
                />
            </div>
            <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
                <button type="button" className="btn btn-secondary" onClick={onCancel} style={{ flex: 1 }} disabled={loading}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={loading}>
                    {loading ? 'Saving…' : habit ? 'Save' : 'Add'}
                </button>
            </div>
        </form>
    );
}
