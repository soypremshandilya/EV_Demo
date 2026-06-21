"""
Seed the VoltRide database with 20 realistic records per table.
Run once:  python -m database.seed_data
"""

from database.db import get_connection, init_db

# ── Scooters ────────────────────────────────────────────────
scooters = [
    ("VR-001 Spark",    "MG Road, Bengaluru",           85, "available"),
    ("VR-002 Flash",    "Connaught Place, Delhi",        72, "rented"),
    ("VR-003 Bolt",     "Andheri West, Mumbai",          15, "charging"),
    ("VR-004 Dash",     "Banjara Hills, Hyderabad",      93, "available"),
    ("VR-005 Zoom",     "Koramangala, Bengaluru",        60, "rented"),
    ("VR-006 Blitz",    "Hinjewadi, Pune",               42, "charging"),
    ("VR-007 Surge",    "Whitefield, Bengaluru",         78, "available"),
    ("VR-008 Drift",    "Salt Lake, Kolkata",            55, "rented"),
    ("VR-009 Glide",    "Velachery, Chennai",            30, "charging"),
    ("VR-010 Rapid",    "Jubilee Hills, Hyderabad",      88, "available"),
    ("VR-011 Thunder",  "Indiranagar, Bengaluru",        67, "rented"),
    ("VR-012 Breeze",   "Powai, Mumbai",                 20, "charging"),
    ("VR-013 Nitro",    "Sector 62, Noida",              95, "available"),
    ("VR-014 Turbo",    "Madhapur, Hyderabad",           48, "rented"),
    ("VR-015 Wave",     "T Nagar, Chennai",              12, "charging"),
    ("VR-016 Pulse",    "Viman Nagar, Pune",             80, "available"),
    ("VR-017 Storm",    "Electronic City, Bengaluru",    63, "rented"),
    ("VR-018 Aero",     "Gachibowli, Hyderabad",        35, "charging"),
    ("VR-019 Volt",     "Saket, Delhi",                  90, "available"),
    ("VR-020 Edge",     "Marine Drive, Mumbai",          74, "rented"),
]

# ── Batteries ───────────────────────────────────────────────
batteries = [
    ("MG Road Swap Hub",             92),
    ("Connaught Place Station",      78),
    ("Andheri Charge Dock",          45),
    ("Banjara Hills Depot",          88),
    ("Koramangala Swap Point",       63),
    ("Hinjewadi Energy Bay",         30),
    ("Whitefield Power Kiosk",       95),
    ("Salt Lake Swap Center",        52),
    ("Velachery Battery Dock",       18),
    ("Jubilee Hills Station",        84),
    ("Indiranagar Swap Hub",         70),
    ("Powai Charge Point",           25),
    ("Sector 62 Battery Bay",        97),
    ("Madhapur Swap Depot",          40),
    ("T Nagar Power Station",        15),
    ("Viman Nagar Swap Dock",        82),
    ("Electronic City Hub",          58),
    ("Gachibowli Energy Center",     33),
    ("Saket Swap Station",           91),
    ("Marine Drive Battery Kiosk",   76),
]

# ── Customers ───────────────────────────────────────────────
customers = [
    ("Aarav Sharma",        34,  8500.00),
    ("Priya Patel",         28,  7200.00),
    ("Rohan Mehta",         45,  12500.00),
    ("Sneha Iyer",          12,  3100.00),
    ("Vikram Singh",        51,  14800.00),
    ("Ananya Reddy",        22,  5600.00),
    ("Karthik Nair",        38,  9900.00),
    ("Divya Gupta",         17,  4300.00),
    ("Arjun Das",           63,  18200.00),
    ("Meera Joshi",          9,  2400.00),
    ("Rahul Verma",         41,  11000.00),
    ("Pooja Kulkarni",      30,  7800.00),
    ("Aditya Rao",          55,  15600.00),
    ("Nisha Bhat",          19,  4900.00),
    ("Siddharth Menon",     47,  13200.00),
    ("Kavya Pillai",        25,  6400.00),
    ("Harsh Chopra",        36,  9200.00),
    ("Ritu Deshmukh",       14,  3700.00),
    ("Manish Tiwari",       58,  16800.00),
    ("Lakshmi Venkat",       8,  2100.00),
]

# ── Rentals ─────────────────────────────────────────────────
#  (scooter_id, customer_id, duration_hours, amount)
rentals = [
    ( 2,  1,  2.0,   250.00),
    ( 5,  3,  4.5,   560.00),
    ( 8,  5, 24.0,  1800.00),
    (11,  7,  1.5,   190.00),
    (14,  9,  3.0,   375.00),
    (17, 11,  6.0,   750.00),
    (20, 13, 12.0,  1200.00),
    ( 2,  2,  1.0,   130.00),
    ( 5,  4,  8.0,   950.00),
    ( 8,  6,  2.5,   310.00),
    (11,  8, 48.0,  3200.00),
    (14, 10,  0.5,    75.00),
    (17, 12,  3.0,   375.00),
    (20, 14,  5.0,   625.00),
    ( 2, 15,  1.5,   190.00),
    ( 5, 16, 24.0,  1800.00),
    ( 8, 17,  2.0,   250.00),
    (11, 18,  7.0,   870.00),
    (14, 19,  4.0,   500.00),
    (17, 20,  1.0,   130.00),
]


def seed():
    """Insert all seed data. Safe to call multiple times — clears tables first."""
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    # Clear existing data (order matters for foreign keys)
    for table in ("rentals", "customers", "batteries", "scooters"):
        cur.execute(f"DELETE FROM {table}")

    cur.executemany(
        "INSERT INTO scooters (name, location, battery_percentage, status) VALUES (?, ?, ?, ?)",
        scooters,
    )
    cur.executemany(
        "INSERT INTO batteries (station_name, battery_level) VALUES (?, ?)",
        batteries,
    )
    cur.executemany(
        "INSERT INTO customers (name, total_rides, total_payment) VALUES (?, ?, ?)",
        customers,
    )
    cur.executemany(
        "INSERT INTO rentals (scooter_id, customer_id, duration_hours, amount) VALUES (?, ?, ?, ?)",
        rentals,
    )

    conn.commit()
    conn.close()
    print("Seeded 20 records into each table.")


if __name__ == "__main__":
    seed()
