# 02 · Model

A star schema: one fact table in the middle, three dimensions around it, and a table for the measures. Open Model view to do each step.

## Tables

| Table | Grain (one row per) | Key | Rows |
|---|---|---|---|
| fact_instalment | instalment of a payment | `payment_id` + `instalment_no` | 296,425 |
| dim_date | day, 4 Sep 2016 to 3 May 2020 | `date` | 1,338 |
| dim_payment_method | payment type | `payment_type` | 5 |
| dim_state | customer state | `customer_state` | 27 |
| _Measures | (holds the measures only) | | |

## Mark the date table

Select `dim_date` > Table tools > Mark as date table > Date column: `date`.

## Relationships

Power BI may create some of these on load; check each one (double-click the line) and create any that is missing by dragging the dimension column onto the fact column.

| From (one side) | To (many side) | Cardinality | Cross filter | Active |
|---|---|---|---|---|
| dim_date[date] | fact_instalment[cash_date] | One to many | Single | Yes |
| dim_payment_method[payment_type] | fact_instalment[payment_type] | One to many | Single | Yes |
| dim_state[customer_state] | fact_instalment[customer_state] | One to many | Single | Yes |

There is no relationship on `fact_instalment[order_date]`; it is shown only in the late payments table. If Power BI created one, delete it.

## Hide columns

Right-click > Hide in report view. The report uses the measures and the dimension columns instead.

| Table | Hide |
|---|---|
| fact_instalment | `payment_type`, `customer_state`, `cash_date`, `amount`, `instalment_no` |
| dim_date | `weekday_no` |
| dim_payment_method | `payment_type`, `sort_order` |
| dim_state | `customer_state` |

Visible fact columns: `payment_id`, `order_date`, `instalments`, `status`, `is_late` (used by the late payments table and its filter).

## Sort by column

Select the column > Column tools > Sort by column.

| Column | Sort by |
|---|---|
| dim_date[weekday] | dim_date[weekday_no] |
| dim_payment_method[payment_method] | dim_payment_method[sort_order] |

## Column formats

| Column | Format |
|---|---|
| dim_date[date], fact_instalment[order_date] | `d mmm yyyy` (Column tools > Format > Custom) |
| fact_instalment[instalments] | Whole number, Summarization: Don't summarize |

## Display folders

Each measure in `03-measures.dax` names its folder (Cash, Late, Dates). Select the measure in Model view > Properties > Display folder.
