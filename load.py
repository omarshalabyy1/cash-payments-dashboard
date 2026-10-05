"""Check the client's input files, load them into PostgreSQL, apply the cash rules, build the star schema,
then check that every total still matches the source. Run it again at any time: it rebuilds from scratch."""

from io import StringIO
from pathlib import Path

import pandas as pd
import psycopg

from config import load_config

TABLES = {  # raw table: (its file in client.yaml inputs, the columns it needs)
    "raw.orders": ("orders", ["order_id", "customer_id", "order_purchase_timestamp", "order_approved_at"]),
    "raw.order_payments": ("payments", ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"]),
    "raw.customers": ("customers", ["customer_id", "customer_state"]),
    "raw.payment_methods": ("payment_methods", ["payment_type", "payment_method", "sort_order"]),
    "raw.regions": ("regions", ["customer_state", "state", "region"]),
}


def run_sql(conn, name):
    conn.execute(Path("sql", name).read_text(encoding="utf-8"))
    print(f"ran sql/{name}")


cfg = load_config()

# The input check: every file is there and has its columns, before anything in the database changes.
frames = {}
for table, (key, columns) in TABLES.items():
    path = cfg["input_dir"] / cfg["inputs"][key]
    if not path.exists():
        raise SystemExit(f"missing input file data/input/{path.name} (inputs.{key} in config/client.yaml)")
    missing = [c for c in columns if c not in pd.read_csv(path, nrows=0).columns]
    if missing:
        raise SystemExit(f"data/input/{path.name} is missing column(s): {', '.join(missing)}")
    frames[table] = pd.read_csv(path, usecols=columns, dtype=str)[columns]

with psycopg.connect(cfg["db_url"]) as conn:
    run_sql(conn, "1_load.sql")
    for table, df in frames.items():
        with conn.cursor().copy(f"COPY {table} ({', '.join(df.columns)}) FROM STDIN WITH (FORMAT csv)") as copy:
            copy.write(df.to_csv(index=False, header=False))
        print(f"loaded {table}: {len(df):,} rows")

    conn.execute("select set_config('client.late_after_days', %s, false)", [str(cfg["rules"]["late_after_days"])])
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
