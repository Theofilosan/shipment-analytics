with source as (
    select * from {{ source('raw', 'shipments') }}
)

select
    shipment_id,
    customer_id,
    carrier_id,
    origin,
    destination,
    cast(ship_date as date) as ship_date,
    cast(promised_delivery_date as date) as promised_delivery_date,
    cast(actual_delivery_date as date) as actual_delivery_date,
    datediff(
        'day',
        cast(promised_delivery_date as date),
        cast(actual_delivery_date as date)
    ) as delay_days,
    weight_kg,
    cost,
    status
from source
