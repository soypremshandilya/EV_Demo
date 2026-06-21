"""READ-ONLY routes for rentals."""

from fastapi import APIRouter
from database.db import get_connection

router = APIRouter(prefix="/rentals", tags=["Rentals"])


@router.get("")
async def list_rentals():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rentals").fetchall()
    conn.close()
    return [dict(row) for row in rows]
