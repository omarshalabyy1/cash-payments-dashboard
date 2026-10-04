"""Load the orders, payments and customers into PostgreSQL, apply the cash rules, build the star schema,
then check that every total still matches the source. Run it again at any time: it rebuilds from scratch."""

from pathlib import Path

import psycopg

DB = "postgresql://cash:cash@localhost:5434/cash"
RAW = Path("data/raw")
SOURCES = {
    "raw.orders": "olist_orders_dataset.csv",
    "raw.order_payments": "olist_order_payments_dataset.csv",
    "raw.customers": "olist_customers_dataset.csv",
}


def run_sql(conn, name):
    conn.execute(Path("sql", name).read_text(encoding="utf-8"))
    print(f"ran sql/{name}")


with psycopg.connect(DB) as conn:
    run_sql(conn, "1_load.sql")
    for table, file in SOURCES.items():
        with conn.cursor().copy(f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)") as copy:
            copy.write((RAW / file).read_bytes())
        rows = conn.execute(f"select count(*) from {table}").fetchone()[0]
        print(f"loaded {table}: {rows:,} rows")

    run_sql(conn, "2_rules.sql")
    run_sql(conn, "3_model.sql")

    # The check: the model must hold every source payment, and its money must add up to the cent.
    source_payments, source_total = conn.execute(
        "select count(*), sum(payment_value) from raw.order_payments"
    ).fetchone()
    model_payments, received, due, never_paid = conn.execute("""
        select count(distinct payment_id),
               coalesce(sum(amount) filter (where status = 'Received'), 0),
               coalesce(sum(amount) filter (where status = 'Due'), 0),
               coalesce(sum(amount) filter (where status = 'Never paid'), 0)
        from mart.fact_instalment
    """).fetchone()

    print(f"payments: source {source_payments:,}, model {model_payments:,}")
    print(f"source {source_total:,} = received {received:,} + due {due:,} + never paid {never_paid:,}")
    if model_payments != source_payments or received + due + never_paid != source_total:
        raise SystemExit("CHECK FAILED: the model does not match the source")
    print("check passed: every payment is in the model and every total matches the source")
