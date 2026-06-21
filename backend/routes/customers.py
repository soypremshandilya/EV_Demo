"""READ-ONLY routes for customers."""

from fastapi import APIRouter
from database.db import get_connection

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("")
async def list_customers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM customers").fetchall()
    conn.close()
    return [dict(row) for row in rows]
