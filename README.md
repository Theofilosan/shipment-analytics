# Shipment Analytics

End-to-end analytics engineering project: synthetic shipment data -> Python ingestion -> DuckDB warehouse -> dbt models (staging, marts, tests) -> Airflow orchestration -> CI.

Built to practice the modern data-engineering workflow on a small, self-contained stack.

## Architecture

```
generate_data.py     load_duckdb.py             dbt                    Airflow
       |                    |                    |                      |
synthetic CSVs --> DuckDB raw tables --> staging + marts models --> daily DAG runs
(data/raw/)      (warehouse.duckdb)    + tests                  the whole pipeline
```

## Repo layout

| Path | What lives here |
|---|---|
| `generate_data.py` | Synthetic shipment-data generator (seeded, deterministic) |
| `load_duckdb.py` | Loads the raw CSVs into `warehouse.duckdb` |
| `data/raw/` | Generated CSVs (gitignored, created by the generator) |
| `dbt/` | dbt project: sources, staging, marts, tests |
| `airflow/dags/` | Airflow DAG that orchestrates the pipeline |
| `.github/workflows/` | CI: generate -> load -> dbt build |

## Prerequisites

- Python 3.10+
- Git

## Milestone 1 - data in, first query out (under an hour)

```bash
git clone <this repo> && cd shipment-analytics
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python generate_data.py     # writes data/raw/*.csv
python load_duckdb.py       # builds warehouse.duckdb, prints a sample query
```

Done when `warehouse.duckdb` exists and the script prints the top-lanes result.

Then play with the data directly:

```bash
duckdb warehouse.duckdb -c "select status, count(*) from raw.shipments group by 1 order by 2 desc;"
```

Answer these with SQL before moving on:

- What is the average delivery delay per carrier?
- Which lane (origin -> destination) moves the most weight?
- What share of shipments are cancelled, by month?

## Milestone 2 - dbt staging

1. Copy `dbt/profiles.yml.example` to `~/.dbt/profiles.yml`
2. `cd dbt && dbt debug` to check the connection
3. Write `stg_customers.sql` and `stg_carriers.sql` in `models/staging/`, following `stg_shipments.sql`
4. `dbt run` and `dbt test`

Done when all staging models build and their tests pass.

## Milestone 3 - marts: dimensions and facts

1. Build `dim_customers`, `dim_carriers` and `fct_shipments` in `models/marts/` (see the README in that folder)
2. Add tests: unique / not_null on keys, relationships from facts to dims
3. Add one custom test of your own (e.g. `delay_days` is never negative for delivered shipments)

Done when `dbt build` runs green end to end.

## Milestone 4 - Airflow orchestration

1. Install Airflow locally (instructions at the top of `airflow/dags/shipment_pipeline.py`)
2. Fill in the TODOs in the DAG: generate -> load -> dbt run -> dbt test, with retries
3. Trigger the DAG twice for the same logical date and prove it is rerun-safe (no duplicate rows)

Done when the DAG goes green twice in a row and a task re-run changes nothing.

## Milestone 5 - CI and polish

1. Push - GitHub Actions runs the whole pipeline on every push
2. Break something on purpose (drop a not-null column) and watch CI catch it
3. Update this README with final row counts and a screenshot of the DAG graph

## Design decisions

- DuckDB instead of Postgres: zero setup, still real SQL and a real dbt adapter
- Seeded generator: local runs and CI produce identical data, so tests are stable
- dbt-duckdb: same workflow (sources -> staging -> marts -> tests) as on Snowflake or BigQuery

## Assumptions

- All data is synthetic and generated locally; nothing external is fetched
- `delay_days` = actual delivery date minus promised delivery date; a shipment is late when `delay_days > 0`
- In-transit and cancelled shipments have no actual delivery date
