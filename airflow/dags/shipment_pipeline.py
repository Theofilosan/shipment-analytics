"""Shipment analytics pipeline DAG.

Milestone 4: fill in the TODOs, then trigger the DAG twice for the same
logical date and confirm the pipeline is rerun-safe (no duplicate rows).

Local setup (quickest path):

    pip install "apache-airflow==2.10.*" \
        --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.10.txt"
    export AIRFLOW_HOME="$PWD/airflow"
    airflow standalone   # prints the admin password, serves on localhost:8080

Copy this file into $AIRFLOW_HOME/dags/ (or point Airflow's dags_folder here).
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

# TODO: point this at wherever you cloned the repo on your machine.
REPO_DIR = "/path/to/shipment-analytics"

with DAG(
    dag_id="shipment_pipeline",
    description="Generate shipment data, load DuckDB, run dbt models and tests.",
    start_date=datetime(2026, 9, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        # TODO: add retries and a retry_delay - failed tasks should recover on their own.
    },
    tags=["shipment-analytics"],
) as dag:

    generate = BashOperator(
        task_id="generate_data",
        bash_command=f"cd {REPO_DIR} && python generate_data.py",
    )

    load = BashOperator(
        task_id="load_duckdb",
        bash_command=f"cd {REPO_DIR} && python load_duckdb.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {REPO_DIR}/dbt && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {REPO_DIR}/dbt && dbt test",
    )

    # TODO: wire the dependencies so each step waits for the previous one.
