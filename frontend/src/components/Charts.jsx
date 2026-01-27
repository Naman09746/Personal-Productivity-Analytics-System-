import { Bar, Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' }, min: 0, max: 100 }
    }
};

export function WeeklyChart({ dailyRates, labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] }) {
    const data = {
        labels,
        datasets: [{
            data: dailyRates,
            backgroundColor: dailyRates.map(v => v >= 80 ? '#34d399' : v >= 50 ? '#fbbf24' : '#f87171'),
            borderRadius: 4
        }]
    };

    return (
        <div className="chart-container">
            <Bar data={data} options={chartOptions} />
        </div>
    );
}

export function TrendChart({ trends }) {
    if (!trends) return null;

    const data = {
        labels: trends.labels,
        datasets: [
            { label: 'Completion', data: trends.completion_rates, borderColor: '#4f9cf0', tension: 0.3 },
            { label: 'Weighted', data: trends.weighted_scores, borderColor: '#34d399', tension: 0.3 }
        ]
    };

    return (
        <div className="chart-container">
            <Line data={data} options={{ ...chartOptions, plugins: { legend: { display: true, labels: { color: '#94a3b8' } } } }} />
        </div>
    );
}
