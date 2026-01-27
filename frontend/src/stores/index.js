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
    error: null,

    fetchHabits: async () => {
        set({ loading: true });
        try {
            const habits = await api.getHabits();
            set({ habits, loading: false });
        } catch (e) {
            set({ error: e.message, loading: false });
        }
    },

    fetchTodayEntries: async () => {
        set({ loading: true });
        try {
            const data = await api.getTodayEntries();
            set({ todayEntries: data, loading: false });
        } catch (e) {
            set({ error: e.message, loading: false });
        }
    },

    toggleHabit: async (habitId, date, completed) => {
        try {
            await api.createEntry(habitId, date, completed);
            await get().fetchTodayEntries();
        } catch (e) {
            set({ error: e.message });
        }
    },

    createHabit: async (habit) => {
        try {
            await api.createHabit(habit);
            await get().fetchHabits();
            return true;
        } catch (e) {
            set({ error: e.message });
            return false;
        }
    },

    deleteHabit: async (id) => {
        try {
            await api.deleteHabit(id);
            await get().fetchHabits();
        } catch (e) {
            set({ error: e.message });
        }
    }
}));

export const useAnalyticsStore = create((set) => ({
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
    }
}));
