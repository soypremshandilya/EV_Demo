"""READ-ONLY routes for scooters."""

from fastapi import APIRouter
from database.db import get_connection

router = APIRouter(prefix="/scooters", tags=["Scooters"])


@router.get("")
async def list_scooters():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM scooters").fetchall()
    conn.close()
    return [dict(row) for row in rows]
