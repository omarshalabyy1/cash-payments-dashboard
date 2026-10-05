# Input files

The five files the client supplies, as CSV with a header row, UTF-8. The file names are set in `config/client.yaml` under `inputs`.
Extra columns are ignored. `python load.py` stops with a one-line message if a file is missing or a required column is not there.

## orders (`inputs.orders`)

One row per order.

| Column | Type | Example |
|---|---|---|
| order_id | text, unique | e481f51cbdc54678b7cc49136f2d6af7 |
| customer_id | text, in customers | 9ef432eb6251297304e76186b10a928d |
| order_purchase_timestamp | timestamp | 2017-10-02 10:56:33 |
| order_approved_at | timestamp, empty if the payment was never confirmed | 2017-10-02 11:07:15 |

## payments (`inputs.payments`)

One row per payment of an order (an order paid two ways has two rows).

| Column | Type | Example |
|---|---|---|
| order_id | text, in orders | b81ef226f3fe1789b1e8b2acac839d17 |
| payment_sequential | whole number, 1, 2 ... within the order | 1 |
| payment_type | text, in payment_methods | credit_card |
| payment_installments | whole number (0 is read as 1) | 8 |
| payment_value | decimal | 99.33 |

## customers (`inputs.customers`)

| Column | Type | Example |
|---|---|---|
| customer_id | text, unique | 06b8999e2fba1a1fbc88172c00ba8bc7 |
| customer_state | text, in regions | SP |

## payment_methods (`inputs.payment_methods`)

Every `payment_type` that appears in payments, with the name the report shows.

| Column | Type | Example |
|---|---|---|
| payment_type | text, unique | credit_card |
| payment_method | text | Credit card |
| sort_order | whole number | 1 |

## regions (`inputs.regions`)

Every `customer_state` that appears in customers, with its name and region.

| Column | Type | Example |
|---|---|---|
| customer_state | text, unique (any length) | SP |
| state | text | São Paulo |
| region | text | Southeast |

## The demo files

`payment_methods.csv` and `regions.csv` are committed. The other three are the Olist files from Kaggle (see Data in the main README); download them into this folder. They are not committed.
