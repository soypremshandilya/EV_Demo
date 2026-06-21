# Backend — VoltRide AI

FastAPI backend for the EV scooter subscription assistant.

## Structure

```
backend/
├── main.py          # FastAPI app entry point
├── requirements.txt # Python dependencies
├── routes/          # API route handlers
├── database/        # SQLite connection & queries
├── services/        # Business logic layer
├── models/          # Pydantic schemas
└── tools/           # Gemini function-calling tools
```

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
