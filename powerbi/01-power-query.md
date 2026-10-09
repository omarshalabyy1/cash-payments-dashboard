# 01 · Power Query

Five queries: one connection query, and four that load the star schema from the Semantic layer (schema `semantic`).
For each one: Home > Get data > Blank query, then Home > Advanced Editor, paste the code, Done, and rename the query (right-click > Rename) to the name in the heading.

The server, database and user are the `warehouse` values in `config/client.yaml`; the code below has the demo values (port 5434, `cash`). For a client, change them in the Warehouse query only.
The first time, Power BI asks for credentials: choose **Database**, user = `warehouse.user`, password = `DB_PASSWORD` in `.env` (demo: `cash` and `cash`).
If it asks about encryption, choose to connect without it (the database runs only on your laptop).

| Query | Load | Rows | Why |
|---|---|---|---|
| Warehouse | No (Enable load off) | | The connection, written once so every table uses the same server |
| fact_instalment | Yes | 296,425 | The fact table |
| dim_date | Yes | 1,827 | The calendar, built in SQL from the fixed range in `config/client.yaml`, so the notebook and the report share one |
| dim_payment_method | Yes | 5 | Readable method names and their order |
| dim_state | Yes | 27 | State names and the region each belongs to |

No column is renamed: the names come from the warehouse, so a query, a measure and the SQL checks all use the same words.

## Warehouse (connection only, do not load)

The connection to the warehouse, written once. Right-click the query and untick **Enable load**, so it does not become a table.

```m
let
    Source = PostgreSQL.Database("127.0.0.1:5434", "cash")
in
    Source
```

## fact_instalment (load)

One row per instalment of a payment. `order_id` is left out: `payment_id` already holds it and the report never uses it.

```m
let
    Source = Warehouse,
    Navigation = Source{[Schema = "semantic", Item = "fact_instalment"]}[Data],
    #"Selected Columns" = Table.SelectColumns(Navigation, {
        "payment_id", "instalment_no", "instalments", "payment_type", "customer_state",
        "order_date", "cash_date", "amount", "status", "is_late"
    }),
    #"Changed Type" = Table.TransformColumnTypes(#"Selected Columns", {
        {"payment_id", type text},
        {"instalment_no", Int64.Type},
        {"instalments", Int64.Type},
        {"payment_type", type text},
        {"customer_state", type text},
        {"order_date", type date},
        {"cash_date", type date},
        {"amount", Currency.Type},
        {"status", type text},
        {"is_late", type logical}
    })
in
    #"Changed Type"
```

| Step | What it does |
|---|---|
| Source | Starts from the Warehouse connection |
| Navigation | Opens the table `semantic.fact_instalment` |
| Selected Columns | Keeps the ten columns the model needs |
| Changed Type | Sets each type; `amount` is Fixed decimal number (`Currency.Type`) so money adds up to the cent |

## dim_date (load)

One row per day of the fixed range `calendar.start` to `calendar.end` in `config/client.yaml` (demo: 1 Jan 2016 to 31 Dec 2020). It covers the first order (4 Sep 2016) and the last instalment (3 May 2020); it is never read from the fact table.

```m
let
    Source = Warehouse,
    Navigation = Source{[Schema = "semantic", Item = "dim_date"]}[Data],
    #"Selected Columns" = Table.SelectColumns(Navigation, {"date", "year", "year_month", "weekday", "weekday_no"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Selected Columns", {
        {"date", type date},
        {"year", Int64.Type},
        {"year_month", type text},
        {"weekday", type text},
        {"weekday_no", Int64.Type}
    })
in
    #"Changed Type"
```

## dim_payment_method (load)

One row per payment type (5 rows).

```m
let
    Source = Warehouse,
    Navigation = Source{[Schema = "semantic", Item = "dim_payment_method"]}[Data],
    #"Selected Columns" = Table.SelectColumns(Navigation, {"payment_type", "payment_method", "sort_order"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Selected Columns", {
        {"payment_type", type text},
        {"payment_method", type text},
        {"sort_order", Int64.Type}
    })
in
    #"Changed Type"
```

## dim_state (load)

One row per customer state (27 rows), with its region.

```m
let
    Source = Warehouse,
    Navigation = Source{[Schema = "semantic", Item = "dim_state"]}[Data],
    #"Selected Columns" = Table.SelectColumns(Navigation, {"customer_state", "state", "region"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Selected Columns", {
        {"customer_state", type text},
        {"state", type text},
        {"region", type text}
    })
in
    #"Changed Type"
```

Then Home > Close & Apply. Expected row counts (Table view, bottom left): fact_instalment 296,425; dim_date 1,827; dim_payment_method 5; dim_state 27.

## _Measures (load)

A table that only holds the measures. Home > Enter data, name it `_Measures`, click Load. After you paste the first measure into it (step 03), delete its `Column1`.
