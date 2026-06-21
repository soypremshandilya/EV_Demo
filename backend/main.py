from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from routes.scooters import router as scooters_router
from routes.batteries import router as batteries_router
from routes.customers import router as customers_router
from routes.rentals import router as rentals_router

app = FastAPI(
    title="VoltRide AI API",
    description="Internal AI assistant API for EV scooter subscription operations. READ ONLY.",
    version="0.1.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Ensure tables exist on startup
init_db()

# READ-ONLY route registration
app.include_router(scooters_router)
app.include_router(batteries_router)
app.include_router(customers_router)
app.include_router(rentals_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "voltride-ai-api"}
