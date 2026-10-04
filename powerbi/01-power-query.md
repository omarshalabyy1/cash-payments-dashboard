# 01 · Power Query

Five queries: one staging query that holds the connection, and four that load the star schema.
For each one: Home > Get data > Blank query, then Home > Advanced Editor, paste the code, Done, and rename the query (right-click > Rename) to the name in the heading.

The first time, Power BI asks for credentials: choose **Database**, user `cash`, password `cash`.
If it asks about encryption, choose to connect without it (the database runs only on your laptop).

## Warehouse (staging, do not load)

The connection to the warehouse, written once. Right-click the query and untick **Enable load**, so it does not become a table.

```m
let
    Source = PostgreSQL.Database("localhost:5434", "cash")
in
    Source
```

## fact_instalment (load)

One row per instalment of a payment. `order_id` is left out: `payment_id` already holds it and the report never uses it.

```m
let
    Source = Warehouse,
    Navigation = Source{[Schema = "mart", Item = "fact_instalment"]}[Data],
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
| Navigation | Opens the table `mart.fact_instalment` |
| Selected Columns | Keeps the ten columns the model needs |
| Changed Type | Sets each type; `amount` is Fixed decimal number (`Currency.Type`) so money adds up to the cent |

## dim_date (load)

One row per day, from the first order (4 Sep 2016) to the last instalment (3 May 2020).

```m
let
    Source = Warehouse,
    Navigation = Source{[Schema = "mart", Item = "dim_date"]}[Data],
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
    Navigation = Source{[Schema = "mart", Item = "dim_payment_method"]}[Data],
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
    Navigation = Source{[Schema = "mart", Item = "dim_state"]}[Data],
    #"Selected Columns" = Table.SelectColumns(Navigation, {"customer_state", "state", "region"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Selected Columns", {
        {"customer_state", type text},
        {"state", type text},
        {"region", type text}
    })
in
    #"Changed Type"
```

Then Home > Close & Apply. Expected row counts (Table view, bottom left): fact_instalment 296,425; dim_date 1,338; dim_payment_method 5; dim_state 27.

## _Measures (load)

A table that only holds the measures. Home > Enter data, name it `_Measures`, click Load. After you paste the first measure into it (step 03), delete its `Column1`.
