import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores';
import { Navbar } from './components/Navbar';
import { LoginPage, RegisterPage } from './pages/AuthPages';
import { DashboardPage } from './pages/DashboardPage';
import { TodayPage } from './pages/TodayPage';
import { WeeklyPage } from './pages/WeeklyPage';
import { MonthlyPage } from './pages/MonthlyPage';
import './index.css';

function PrivateRoute({ children }) {
  const isAuthenticated = useAuthStore(s => s.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function Layout({ children }) {
  return (
    <div className="app-container" style={{ flexDirection: 'column' }}>
      <Navbar />
      <main className="main-content">{children}</main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={<PrivateRoute><Layout><DashboardPage /></Layout></PrivateRoute>} />
        <Route path="/today" element={<PrivateRoute><Layout><TodayPage /></Layout></PrivateRoute>} />
        <Route path="/weekly" element={<PrivateRoute><Layout><WeeklyPage /></Layout></PrivateRoute>} />
        <Route path="/monthly" element={<PrivateRoute><Layout><MonthlyPage /></Layout></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
