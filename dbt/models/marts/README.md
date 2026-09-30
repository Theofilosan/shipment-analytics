# Marts (Milestone 3)

Build these three models here:

- `dim_customers.sql` - one row per customer, from `stg_customers`
- `dim_carriers.sql` - one row per carrier, from `stg_carriers`
- `fct_shipments.sql` - one row per shipment, from `stg_shipments`, with measures like `weight_kg`, `cost`, `delay_days`

Then add a `schema.yml` with tests:

- unique + not_null on every key
- `relationships` tests from `fct_shipments.customer_id` -> `dim_customers.customer_id` (same for carrier)
- one custom test of your own, e.g. `delay_days >= 0` when status is `delivered`

Materialization is set to `table` in `dbt_project.yml`.
