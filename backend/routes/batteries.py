"""READ-ONLY routes for batteries."""

from fastapi import APIRouter
from database.db import get_connection

router = APIRouter(prefix="/batteries", tags=["Batteries"])


@router.get("")
async def list_batteries():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM batteries").fetchall()
    conn.close()
    return [dict(row) for row in rows]
