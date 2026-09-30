"""Generate synthetic shipment data.

Usage: python generate_data.py [--rows 2000] [--seed 42]

Writes customers.csv, carriers.csv and shipments.csv to data/raw/.
Deterministic for a given seed, so local runs and CI produce the same data.
"""
import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

CITIES = [
    ("Copenhagen", "Denmark"),
    ("Aarhus", "Denmark"),
    ("Hamburg", "Germany"),
    ("Rotterdam", "Netherlands"),
    ("Oslo", "Norway"),
    ("Stockholm", "Sweden"),
    ("Gdansk", "Poland"),
    ("Felixstowe", "United Kingdom"),
    ("Antwerp", "Belgium"),
    ("Helsinki", "Finland"),
]
SEGMENTS = ["retail", "manufacturing", "pharma", "food", "electronics"]
CARRIERS = [
    ("Nord Freight", "road", 0.92),
    ("Baltic Lines", "sea", 0.41),
    ("ScanHaul", "road", 0.85),
    ("Meridian Transport", "rail", 0.63),
    ("Kyst Logistics", "sea", 0.47),
    ("Polar Cargo", "road", 1.05),
]
FIRST = ["Astrid", "Lars", "Freja", "Mikkel", "Sofia", "Emil", "Ida", "Oscar", "Nora", "Felix"]
LAST = ["Hansen", "Larsen", "Jensen", "Nielsen", "Pedersen", "Andersen", "Madsen", "Holm", "Berg", "Lund"]
STATUSES = ["delivered", "delivered", "delivered", "delivered", "in_transit", "cancelled"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    out = Path("data/raw")
    out.mkdir(parents=True, exist_ok=True)

    customers = []
    for i in range(1, 61):
        city, country = rng.choice(CITIES)
        customers.append({
            "customer_id": i,
            "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
            "city": city,
            "country": country,
            "segment": rng.choice(SEGMENTS),
            "signup_date": (date(2024, 1, 1) + timedelta(days=rng.randint(0, 500))).isoformat(),
        })

    carriers = []
    for i, (name, mode, rate) in enumerate(CARRIERS, start=1):
        carriers.append({
            "carrier_id": i,
            "name": name,
            "mode": mode,
            "base_rate_per_kg": rate,
        })

    start = date(2025, 1, 1)
    shipments = []
    for i in range(1, args.rows + 1):
        origin, _ = rng.choice(CITIES)
        destination, _ = rng.choice(CITIES)
        while destination == origin:
            destination, _ = rng.choice(CITIES)
        ship_date = start + timedelta(days=rng.randint(0, 540))
        transit_days = rng.randint(1, 12)
        promised = ship_date + timedelta(days=transit_days)
        status = rng.choice(STATUSES)
        if status == "delivered":
            actual = promised + timedelta(days=rng.choice([-2, -1, 0, 0, 0, 1, 2, 3]))
            actual = actual.isoformat()
        else:
            actual = ""
        carrier = rng.choice(carriers)
        weight = round(rng.uniform(5, 2500), 1)
        cost = round(weight * carrier["base_rate_per_kg"] * rng.uniform(0.9, 1.4), 2)
        shipments.append({
            "shipment_id": i,
            "customer_id": rng.randint(1, len(customers)),
            "carrier_id": carrier["carrier_id"],
            "origin": origin,
            "destination": destination,
            "ship_date": ship_date.isoformat(),
            "promised_delivery_date": promised.isoformat(),
            "actual_delivery_date": actual,
            "weight_kg": weight,
            "cost": cost,
            "status": status,
        })

    for name, rows in [("customers", customers), ("carriers", carriers), ("shipments", shipments)]:
        path = out / f"{name}.csv"
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
