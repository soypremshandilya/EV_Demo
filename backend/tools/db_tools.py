"""
Read-only database tools for Gemini function calling.

Every function here runs SELECT queries ONLY.
No INSERT, UPDATE, or DELETE is ever used.
"""

from database.db import get_connection


def get_all_scooters() -> list[dict]:
    """Return all scooters with their id, name, location, battery percentage, and status."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, location, battery_percentage, status FROM scooters"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_low_battery_scooters() -> list[dict]:
    """Return scooters with battery percentage below 30%."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, location, battery_percentage, status "
        "FROM scooters WHERE battery_percentage < 30"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_available_scooters() -> list[dict]:
    """Return scooters that currently have status 'available'."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, location, battery_percentage, status "
        "FROM scooters WHERE status = 'available'"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_customers() -> list[dict]:
    """Return all customers with their id, name, total rides, and total payment."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, total_rides, total_payment FROM customers"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_customers() -> list[dict]:
    """Return the top 5 customers ranked by total payment (highest first)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, total_rides, total_payment "
        "FROM customers ORDER BY total_payment DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_rentals() -> list[dict]:
    """Return all rental records with id, scooter_id, customer_id, duration in hours, and amount."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, scooter_id, customer_id, duration_hours, amount FROM rentals"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_low_battery_stations() -> list[dict]:
    """Return battery swap stations with battery level below 30%."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, station_name, battery_level "
        "FROM batteries WHERE battery_level < 30"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
