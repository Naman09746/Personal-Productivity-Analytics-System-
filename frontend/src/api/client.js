const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('access_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    async request(endpoint, options = {}) {
        const headers = { 'Content-Type': 'application/json', ...options.headers };
        if (this.token) headers['Authorization'] = `Bearer ${this.token}`;

        const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

        if (response.status === 401) {
            const refreshed = await this.refreshToken();
            if (refreshed) return this.request(endpoint, options);
            this.clearToken();
            window.location.href = '/login';
            throw new Error('Session expired');
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Request failed');
        }

        return response.status === 204 ? null : response.json();
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${API_BASE}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.setToken(data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                return true;
            }
        } catch (e) { console.error('Refresh failed:', e); }
        return false;
    }

    // Auth
    async register(email, password, name) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, name })
        });
        this.setToken(data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        return data;
    }

    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        this.setToken(data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        return data;
    }

    logout() { this.clearToken(); }

    // Habits
    getHabits() { return this.request('/habits'); }
    createHabit(habit) { return this.request('/habits', { method: 'POST', body: JSON.stringify(habit) }); }
    updateHabit(id, habit) { return this.request(`/habits/${id}`, { method: 'PUT', body: JSON.stringify(habit) }); }
    deleteHabit(id) { return this.request(`/habits/${id}`, { method: 'DELETE' }); }

    // Entries
    getTodayEntries() { return this.request('/entries/today'); }
    getDateEntries(date) { return this.request(`/entries/date/${date}`); }
    getWeekEntries(weekStart) { return this.request(`/entries/week/${weekStart}`); }
    createEntry(habitId, date, completed) {
        return this.request('/entries', { method: 'POST', body: JSON.stringify({ habit_id: habitId, entry_date: date, completed }) });
    }

    // Analytics
    getTodayStats() { return this.request('/analytics/today'); }
    getWeekAnalytics(weekStart) { return weekStart ? this.request(`/analytics/week/${weekStart}`) : this.request('/analytics/week'); }
    getMonthAnalytics(year, month) { return year ? this.request(`/analytics/month/${year}/${month}`) : this.request('/analytics/month'); }
    getTrends(period = 'weekly', lookback = 8) { return this.request(`/analytics/trends?period=${period}&lookback=${lookback}`); }
}

export const api = new ApiClient();
export default api;
