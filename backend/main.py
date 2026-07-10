import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from routes.scooters import router as scooters_router
from routes.batteries import router as batteries_router
from routes.customers import router as customers_router
from routes.rentals import router as rentals_router
from services.simulator import run_simulator
from routes.chat import router as chat_router
from routes.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app):
    """Start the data simulator on startup, cancel on shutdown."""
    task = asyncio.create_task(run_simulator())
    yield
    task.cancel()


app = FastAPI(
    title="VoltRide AI API",
    description="Internal AI assistant API for EV scooter subscription operations. READ ONLY.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend (localhost for dev, env var for production)
origins = ["http://localhost:5173"]
extra = os.getenv("CORS_ORIGINS", "")
if extra:
    origins.extend([o.strip() for o in extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Ensure tables exist on startup
init_db()

# Auto-seed if tables are empty (handles fresh deployments)
from database.db import get_connection
_conn = get_connection()
_count = _conn.execute("SELECT COUNT(*) FROM scooters").fetchone()[0]
_conn.close()
if _count == 0:
    from database.seed_data import seed
    seed()
    print("Database seeded with sample data.")

# READ-ONLY route registration
app.include_router(scooters_router)
app.include_router(batteries_router)
app.include_router(customers_router)
app.include_router(rentals_router)
app.include_router(chat_router)
app.include_router(dashboard_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "voltride-ai-api"}

