"""
Background data simulator — mutates DB every 30 seconds to mimic live operations.

Updates:
  • scooters.battery_percentage  — random drift ±5 (clamped 0–100)
  • batteries.battery_level      — random drift ±8 (clamped 0–100)
  • customers.total_rides        — 30% chance of +1 per customer
  • rentals.duration_hours       — small random increment (0.1–0.5) on ~40% of rentals
"""

import asyncio
import random
from database.db import get_connection

INTERVAL_SECONDS = 30


def _tick():
    """Run one simulation cycle."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Scooter battery drift ──
    scooters = cur.execute("SELECT id, battery_percentage FROM scooters").fetchall()
    for row in scooters:
        delta = random.randint(-5, 5)
        new_val = max(0, min(100, row["battery_percentage"] + delta))
        cur.execute("UPDATE scooters SET battery_percentage = ? WHERE id = ?", (new_val, row["id"]))

    # ── Battery level drift ──
    batteries = cur.execute("SELECT id, battery_level FROM batteries").fetchall()
    for row in batteries:
        delta = random.randint(-8, 8)
        new_val = max(0, min(100, row["battery_level"] + delta))
        cur.execute("UPDATE batteries SET battery_level = ? WHERE id = ?", (new_val, row["id"]))

    # ── Customer ride bumps (30 % chance each) ──
    customers = cur.execute("SELECT id, total_rides FROM customers").fetchall()
    for row in customers:
        if random.random() < 0.3:
            cur.execute(
                "UPDATE customers SET total_rides = total_rides + 1 WHERE id = ?",
                (row["id"],),
            )

    # ── Rental duration increments (~40 % of rentals) ──
    rentals = cur.execute("SELECT id FROM rentals").fetchall()
    for row in rentals:
        if random.random() < 0.4:
            bump = round(random.uniform(0.1, 0.5), 1)
            cur.execute(
                "UPDATE rentals SET duration_hours = duration_hours + ? WHERE id = ?",
                (bump, row["id"]),
            )

    conn.commit()
    conn.close()


async def run_simulator():
    """Async loop that calls _tick() every INTERVAL_SECONDS."""
    while True:
        await asyncio.sleep(INTERVAL_SECONDS)
        _tick()
        print(f"[simulator] data refreshed (every {INTERVAL_SECONDS}s)")
