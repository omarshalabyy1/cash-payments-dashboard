"""Check the client's input files, load them into the Bronze layer, build the Silver, Gold, Semantic and Analytical
layers, then check that every total still matches the source. Run it again at any time: it rebuilds from scratch.

Bronze (schema bronze): the columns the rules use, as text, exactly as written in the file, with their lineage
(the file, the row number in it, the run id and the load time). A row whose required value is empty, or whose value
would not convert to the type the Silver layer gives it, is refused: it goes to bronze.quarantine with the reason.
The values are checked with PostgreSQL's own pg_input_is_valid, so every row in Bronze converts in Silver.
An empty file or a key that appears twice stops the run. Every load is written to ops.load_log.
The whole run is one transaction: if anything fails, nothing changes."""

import uuid
from pathlib import Path

import pandas as pd
import psycopg

from config import load_config

TABLES = {  # Bronze table: (its file in client.yaml inputs, the columns it needs)
    "orders": ("orders", ["order_id", "customer_id", "order_purchase_timestamp", "order_approved_at"]),
    "order_payments": ("payments", ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"]),
    "customers": ("customers", ["customer_id", "customer_state"]),
    "payment_methods": ("payment_methods", ["payment_type", "payment_method", "sort_order"]),
    "regions": ("regions", ["customer_state", "state", "region"]),
}

# Bronze table: its key. A key that appears twice stops the run.
KEYS = {
    "orders": ["order_id"],
    "order_payments": ["order_id", "payment_sequential"],
    "customers": ["customer_id"],
    "payment_methods": ["payment_type"],
    "regions": ["customer_state"],
}

# Bronze table: columns that must not be empty (order_approved_at is empty when a payment was never confirmed).
NOT_EMPTY = {table: [c for c in columns if c != "order_approved_at"] for table, (_, columns) in TABLES.items()}

# Bronze table: column: the type the Silver layer gives it.
TYPES = {
    "orders": {"order_purchase_timestamp": "timestamp", "order_approved_at": "timestamp"},
    "order_payments": {"payment_sequential": "integer", "payment_installments": "integer", "payment_value": "numeric(12,2)"},
    "payment_methods": {"sort_order": "integer"},
}


def run_sql(conn, name):
    conn.execute(Path("sql", name).read_text(encoding="utf-8"))
    print(f"ran sql/{name}")


def refusal(table):
    """SQL for the reasons a row is refused, joined with '; '; an empty string when the row is accepted."""
    checks = [f"case when {c} is null then 'missing {c}' end" for c in NOT_EMPTY[table]]
    checks += [f"case when not pg_input_is_valid({c}, '{t}') then '{c} is not a {t}' end"
               for c, t in TYPES.get(table, {}).items()]
    return f"concat_ws('; ', {', '.join(checks)})"


cfg = load_config()

# The input check: every file is there, has its columns and has rows, before anything in the database changes.
# keep_default_na=False keeps every value as written; an empty field still loads as NULL.
frames = {}
for table, (key, columns) in TABLES.items():
    path = cfg["input_dir"] / cfg["inputs"][key]
    if not path.exists():
        raise SystemExit(f"missing input file data/input/{path.name} (inputs.{key} in config/client.yaml)")
    missing = [c for c in columns if c not in pd.read_csv(path, nrows=0).columns]
    if missing:
        raise SystemExit(f"data/input/{path.name} is missing column(s): {', '.join(missing)}")
    df = pd.read_csv(path, usecols=columns, dtype=str, keep_default_na=False)[columns]
    if df.empty:
        raise SystemExit(f"data/input/{path.name} has no rows")
    frames[table] = (path.name, df)

run_id = str(uuid.uuid4())
with psycopg.connect(cfg["db_url"]) as conn:
    conn.execute("create schema if not exists bronze")
    conn.execute("create schema if not exists ops")
    conn.execute("""
        create table if not exists ops.load_log (
            run_id           uuid,
            table_name       text,
            source_file      text,
            rows_in_file     integer,
            rows_loaded      integer,
            rows_quarantined integer,
            loaded_at        timestamptz default now()
        )""")
    conn.execute("drop table if exists bronze.quarantine")
    conn.execute("""
        create table bronze.quarantine (
            table_name  text not null,
            source_file text not null,
            source_row  integer not null,
            row_data    jsonb not null,
            reason      text not null,
            run_id      uuid not null,
            loaded_at   timestamptz not null default now(),
            primary key (table_name, source_row)
        )""")

    for table, (file_name, df) in frames.items():
        columns = TABLES[table][1]
        conn.execute(f"drop table if exists bronze.{table}")
        conn.execute(f"""
            create table bronze.{table} (
                {', '.join(f'{c} text' for c in columns)},
                source_file text not null,
                source_row  integer primary key,   -- the data rows of the file, counted from 1 (the header is not counted)
                run_id      uuid not null,
                loaded_at   timestamptz not null default now()
            )""")
        rows = df.assign(source_file=file_name, source_row=range(1, len(df) + 1), run_id=run_id)
        with conn.cursor().copy(f"copy bronze.{table} ({', '.join(rows.columns)}) from stdin with (format csv)") as copy:
            copy.write(rows.to_csv(index=False, header=False))

        # Refused rows move from the Bronze table to bronze.quarantine, as written in the file.
        refused = conn.execute(f"""
            with refused as (
                delete from bronze.{table}
                where {refusal(table)} <> ''
                returning *, {refusal(table)} as reason
            )
            insert into bronze.quarantine (table_name, source_file, source_row, row_data, reason, run_id)
            select %s, source_file, source_row, jsonb_build_object({', '.join(f"'{c}', {c}" for c in columns)}),
                   reason, run_id
            from refused""", [table]).rowcount

        keys = ", ".join(KEYS[table])
        if conn.execute(f"select count(*) - count(distinct ({keys})) from bronze.{table}").fetchone()[0]:
            raise SystemExit(f"data/input/{file_name}: {' + '.join(KEYS[table])} appears more than once")

        loaded = conn.execute(f"select count(*) from bronze.{table}").fetchone()[0]
        conn.execute(
            "insert into ops.load_log (run_id, table_name, source_file, rows_in_file, rows_loaded, rows_quarantined) "
            "values (%s, %s, %s, %s, %s, %s)", [run_id, table, file_name, len(df), loaded, refused])
        print(f"bronze.{table}: {loaded:,} rows from {file_name}, {refused:,} to bronze.quarantine")

    run_sql(conn, "2_silver.sql")
    # Silver types and keys every Bronze row; it never drops one.
    for table in TABLES:
        lost = conn.execute(f"select (select count(*) from bronze.{table}) - (select count(*) from silver.{table})").fetchone()[0]
        if lost:
            raise SystemExit(f"CHECK FAILED: silver.{table} holds {lost:,} rows fewer than bronze.{table}")

    for name, value in [("late_after_days", cfg["rules"]["late_after_days"]),
                        ("date_start", cfg["calendar"]["start"]), ("date_end", cfg["calendar"]["end"])]:
        conn.execute("select set_config(%s, %s, false)", [f"client.{name}", str(value)])
    run_sql(conn, "3_gold.sql")
    run_sql(conn, "4_semantic.sql")
    run_sql(conn, "5_analytical.sql")

    # The check: the Semantic layer must hold every payment loaded into Bronze, and its money must add up to the cent.
    source_payments, source_total = conn.execute(
        "select count(*), sum(payment_value::numeric(12, 2)) from bronze.order_payments"
    ).fetchone()
    quarantined = conn.execute("select count(*) from bronze.quarantine").fetchone()[0]
    model_payments, received, due, never_paid = conn.execute("""
        select count(distinct payment_id),
               coalesce(sum(amount) filter (where status = 'Received'), 0),
               coalesce(sum(amount) filter (where status = 'Due'), 0),
               coalesce(sum(amount) filter (where status = 'Never paid'), 0)
        from semantic.fact_instalment
    """).fetchone()

    print(f"payments: source {source_payments:,}, model {model_payments:,}; rows in bronze.quarantine: {quarantined:,}")
    print(f"source {source_total:,} = received {received:,} + due {due:,} + never paid {never_paid:,}")
    if model_payments != source_payments or received + due + never_paid != source_total:
        raise SystemExit("CHECK FAILED: the model does not match the source")
    print("check passed: every payment is in the model and every total matches the source")
