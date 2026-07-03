"""GET /dashboard/stats — aggregated metrics for the dashboard cards."""

from fastapi import APIRouter
from database.db import get_connection

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/stats")
def dashboard_stats():
    conn = get_connection()

    total_scooters = conn.execute("SELECT COUNT(*) FROM scooters").fetchone()[0]
    available = conn.execute("SELECT COUNT(*) FROM scooters WHERE status = 'available'").fetchone()[0]
    charging = conn.execute("SELECT COUNT(*) FROM scooters WHERE status = 'charging'").fetchone()[0]
    total_customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    total_revenue = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM rentals").fetchone()[0]
    avg_battery = conn.execute("SELECT COALESCE(AVG(battery_percentage), 0) FROM scooters").fetchone()[0]

    conn.close()

    return {
        "total_scooters": total_scooters,
        "available_scooters": available,
        "charging_scooters": charging,
        "total_customers": total_customers,
        "total_revenue": round(total_revenue, 2),
        "avg_battery": round(avg_battery, 1),
    }
