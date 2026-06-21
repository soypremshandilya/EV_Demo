# VoltRide AI — EV Operations Hub

Internal AI assistant for an EV scooter subscription company. Employees can look up scooters, batteries, customers, and rentals — powered by Google Gemini 2.5 Flash.

> **Read-only** — the AI never modifies data.

## Tech Stack

| Layer    | Tech                  |
|----------|-----------------------|
| Frontend | React + Vite          |
| Backend  | FastAPI               |
| Database | SQLite                |
| AI       | Google Gemini 2.5 Flash |

## Project Structure

```
EV_Demo/
├── frontend/                # React + Vite
│   ├── src/
│   │   ├── components/      # Sidebar
│   │   ├── pages/           # Dashboard, Scooters, Batteries,
│   │   │                    # Customers, Rentals, AI Chat
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   └── package.json
│
├── backend/                 # FastAPI
│   ├── main.py              # App entry point
│   ├── requirements.txt
│   ├── routes/              # GET-only API endpoints
│   ├── database/            # db.py + seed_data.py
│   ├── services/            # Business logic (TBD)
│   ├── models/              # Pydantic schemas (TBD)
│   └── tools/               # Gemini function-calling tools (TBD)
│
└── .gitignore
```

## Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev        # → http://localhost:5173
```

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m database.seed_data   # Create DB + seed 20 records per table
uvicorn main:app --reload      # → http://localhost:8000
```

## API Endpoints

| Method | Endpoint     | Description         |
|--------|--------------|---------------------|
| GET    | /health      | Health check        |
| GET    | /scooters    | List all scooters   |
| GET    | /batteries   | List all batteries  |
| GET    | /customers   | List all customers  |
| GET    | /rentals     | List all rentals    |
