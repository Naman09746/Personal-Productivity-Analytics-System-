import { create } from 'zustand';
import api from '../api/client';

export const useAuthStore = create((set) => ({
    user: null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    loading: false,
    error: null,

    login: async (email, password) => {
        set({ loading: true, error: null });
        try {
            await api.login(email, password);
            set({ isAuthenticated: true, loading: false });
            return true;
        } catch (e) {
            set({ error: e.message, loading: false });
            return false;
        }
    },

    register: async (email, password, name) => {
        set({ loading: true, error: null });
        try {
            await api.register(email, password, name);
            set({ isAuthenticated: true, loading: false });
            return true;
        } catch (e) {
            set({ error: e.message, loading: false });
            return false;
        }
    },

    logout: () => {
        api.logout();
        set({ user: null, isAuthenticated: false });
    },

    clearError: () => set({ error: null })
}));

export const useHabitStore = create((set, get) => ({
    habits: [],
    todayEntries: null,
    loading: false,
    toggleLoadingIds: [], // habitIds being toggled
    error: null,

    fetchHabits: async () => {
        set({ loading: true, error: null });
        try {
            const habits = await api.getHabits();
            set({ habits, loading: false });
        } catch (e) {
            set({ error: e.message, loading: false });
        }
    },

    fetchTodayEntries: async () => {
        set({ loading: true, error: null });
        try {
            const data = await api.getTodayEntries();
            set({ todayEntries: data, loading: false });
        } catch (e) {
            set({ error: e.message, loading: false });
        }
    },

    toggleHabit: async (habitId, date, completed) => {
        const { todayEntries } = get();
        if (!todayEntries) return;

        // Optimistic update
        const prevEntries = JSON.parse(JSON.stringify(todayEntries));
        const updatedHabits = todayEntries.habits.map(h =>
            h.habit_id === habitId ? { ...h, completed } : h
        );
        const completionCount = updatedHabits.filter(h => h.completed).length;
        const total = todayEntries.total_habits || 1;
        const physicalCompleted = updatedHabits.some(h => h.is_physical && h.completed);
        set({
            todayEntries: {
                ...todayEntries,
                habits: updatedHabits,
                completion_count: completionCount,
                completion_rate: (completionCount / total) * 100,
                physical_completed: physicalCompleted
            },
            toggleLoadingIds: [...get().toggleLoadingIds, habitId]
        });

        try {
            await api.createEntry(habitId, date, completed);
            set({ toggleLoadingIds: get().toggleLoadingIds.filter(id => id !== habitId) });
        } catch (e) {
            set({ todayEntries: prevEntries, error: e.message, toggleLoadingIds: [] });
        }
    },

    createHabit: async (habit) => {
        set({ error: null });
        try {
            await api.createHabit(habit);
            await Promise.all([get().fetchHabits(), get().fetchTodayEntries()]);
            return true;
        } catch (e) {
            set({ error: e.message });
            return false;
        }
    },

    updateHabit: async (id, habit) => {
        set({ error: null });
        try {
            await api.updateHabit(id, habit);
            await Promise.all([get().fetchHabits(), get().fetchTodayEntries()]);
            return true;
        } catch (e) {
            set({ error: e.message });
            return false;
        }
    },

    deleteHabit: async (id) => {
        set({ error: null });
        try {
            await api.deleteHabit(id);
            await Promise.all([get().fetchHabits(), get().fetchTodayEntries()]);
            return true;
        } catch (e) {
            set({ error: e.message });
            return false;
        }
    },

    clearError: () => set({ error: null })
}));

export const useAnalyticsStore = create((set, get) => ({
    todayStats: null,
    weeklyData: null,
    monthlyData: null,
    trends: null,
    loading: false,
    error: null,

    fetchTodayStats: async () => {
        try {
            const data = await api.getTodayStats();
            set({ todayStats: data });
        } catch (e) {
            set({ error: e.message });
        }
    },

    fetchWeeklyAnalytics: async (weekStart) => {
        set({ loading: true });
        try {
            const data = await api.getWeekAnalytics(weekStart);
            set({ weeklyData: data, loading: false });
        } catch (e) {
            set({ error: e.message, loading: false });
        }
    },

    fetchMonthlyAnalytics: async (year, month) => {
        set({ loading: true });
        try {
            const data = await api.getMonthAnalytics(year, month);
            set({ monthlyData: data, loading: false });
        } catch (e) {
            set({ error: e.message, loading: false });
        }
    },

    fetchTrends: async (period = 'weekly') => {
        try {
            const data = await api.getTrends(period);
            set({ trends: data });
        } catch (e) {
            set({ error: e.message });
        }
    },

    clearError: () => set({ error: null })
}));
