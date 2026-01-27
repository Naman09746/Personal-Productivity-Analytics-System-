# Personal Productivity Analytics System (PPAS)

A data-driven habit tracking platform emphasizing discipline, consistency, and measurable progress over motivation.

![PPAS Dashboard](docs/screenshots/dashboard.png)

## 🎯 Features

- **Daily Habit Tracking** - Checkbox-based input with rule enforcement
- **Physical Activity Limit** - Only one physical activity per day
- **Automatic Scoring** - Weighted completion rates and consistency metrics
- **Weekly & Monthly Analytics** - Comprehensive performance breakdowns
- **Score Explainability** - Understand why your score changed
- **Goal Thresholds** - Alerts when habits fall below targets
- **Background Jobs** - Automated weekly/monthly report generation

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Zustand, Chart.js |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL |
| Auth | JWT (python-jose), bcrypt |
| Jobs | APScheduler |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create database
createdb ppas

# Start server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker (Recommended)

```bash
docker-compose up -d
```

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   └── middleware/          # Error handling, rate limiting
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── stores/          # Zustand state
│   │   ├── components/      # UI components
│   │   └── pages/           # Route pages
└── docker-compose.yml
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/habits` | List habits |
| POST | `/api/habits` | Create habit |
| POST | `/api/entries` | Log entry |
| GET | `/api/analytics/today` | Today's stats |
| GET | `/api/analytics/week` | Weekly analytics |
| GET | `/api/analytics/month` | Monthly analytics |

Full API docs at `/docs` when running.

## 🔐 Security

- JWT authentication with refresh tokens
- Password hashing (bcrypt)
- Rate limiting (100 req/min)
- Input validation (Pydantic)

## 📈 Resume Description

> **Personal Productivity Analytics System** - Full-stack habit tracking platform with automated performance analytics. Features background job scheduling (APScheduler), rule-based validation, score explainability engine, and goal threshold alerting. Built with FastAPI, PostgreSQL, React, and Zustand.

## 📝 License

MIT
