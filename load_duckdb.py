"""Load the raw CSVs from data/raw/ into warehouse.duckdb and run a sample query."""
import duckdb
from pathlib import Path

RAW = Path("data/raw")
DB = "warehouse.duckdb"


def main():
    con = duckdb.connect(DB)
    con.execute("create schema if not exists raw")
    for table in ["customers", "carriers", "shipments"]:
        csv_path = RAW / f"{table}.csv"
        if not csv_path.exists():
            raise SystemExit(f"missing {csv_path} - run generate_data.py first")
        con.execute(
            f"create or replace table raw.{table} as "
            f"select * from read_csv_auto('{csv_path}', header=true)"
        )
        count = con.execute(f"select count(*) from raw.{table}").fetchone()[0]
        print(f"raw.{table}: {count} rows")

    print("\nTop lanes by total weight:")
    rows = con.execute(
        """
        select origin, destination, count(*) as shipments, round(sum(weight_kg)) as total_kg
        from raw.shipments
        group by 1, 2
        order by total_kg desc
        limit 5
        """
    ).fetchall()
    for origin, destination, n, kg in rows:
        print(f"  {origin} -> {destination}: {n} shipments, {kg} kg")
    con.close()


if __name__ == "__main__":
    main()
