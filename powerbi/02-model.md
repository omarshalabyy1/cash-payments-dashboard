# 02 · Model

A star schema: one fact table in the middle, three dimensions around it, and a table for the measures. Open Model view to do each step.

## Tables

| Table | Grain (one row per) | Key | Rows | Why |
|---|---|---|---|---|
| fact_instalment | instalment of a payment | `payment_id` + `instalment_no` | 296,425 | Money lands on a date per instalment, so cash by day needs this grain |
| dim_date | day, 1 Jan 2016 to 31 Dec 2020 | `date` | 1,827 | A fixed range from `config/client.yaml` (`calendar`), whole years, covering every order and every Still due instalment |
| dim_payment_method | payment type | `payment_type` | 5 | Turns codes like `credit_card` into names and fixes their order |
| dim_state | customer state | `customer_state` | 27 | Gives each state its region, the level the report shows |
| _Measures | (holds the measures only) | | | Keeps the 12 measures in one place, apart from the data |

There are no calculated columns and no calculated tables: every rule is already in the warehouse, in the Gold layer (`sql/3_gold.sql`).

## Mark the date table

Select `dim_date` > Table tools > Mark as date table > Date column: `date`.
Why: Power BI then uses this calendar for every date, not its own hidden ones.

The date table comes from the Semantic layer (`sql/4_semantic.sql`, a fixed range set in `config/client.yaml`, never the MIN and MAX of the fact) through the `dim_date` query in 01; there is no DAX calendar.

## Relationships

Power BI may create some of these on load; check each one (double-click the line) and create any that is missing by dragging the dimension column onto the fact column.

| From (one side) | To (many side) | Cardinality | Cross filter | Active | Why |
|---|---|---|---|---|---|
| dim_date[date] | fact_instalment[cash_date] | One to many | Single | Yes | Cash is reported on the day it lands, not the day the order was placed |
| dim_payment_method[payment_type] | fact_instalment[payment_type] | One to many | Single | Yes | Slice the money by method |
| dim_state[customer_state] | fact_instalment[customer_state] | One to many | Single | Yes | Slice the money by region and state |

Single direction everywhere: dimensions filter the fact, never the other way, so no filter takes a surprising path.

There is no relationship on `fact_instalment[order_date]`; it is shown only in the late payments table. If Power BI created one, delete it.
Why: one date role (the cash date) keeps every date slicer meaning the same thing.

## Hide columns

Right-click > Hide in report view. The report uses the measures and the dimension columns instead.

| Table | Hide | Why |
|---|---|---|
| fact_instalment | `payment_type`, `customer_state`, `cash_date`, `amount`, `instalment_no` | Keys are used through their dimension; `amount` only through measures, so it is never summed by mistake |
| dim_date | `weekday_no` | Only there to sort `weekday` |
| dim_payment_method | `payment_type`, `sort_order` | A key and a sort helper |
| dim_state | `customer_state` | The key; the report shows `state` and `region` |

Visible fact columns: `payment_id`, `order_date`, `instalments`, `status`, `is_late` (used by the late payments table and its filter).

## Sort by column

Select the column > Column tools > Sort by column.

| Column | Sort by | Why |
|---|---|---|
| dim_date[weekday] | dim_date[weekday_no] | Monday to Sunday, not alphabetical |
| dim_payment_method[payment_method] | dim_payment_method[sort_order] | Credit card first, the order used everywhere in the repo |

## Column formats

| Column | Format | Why |
|---|---|---|
| dim_date[date], fact_instalment[order_date] | `d mmm yyyy` (Column tools > Format > Custom) | One date style across the report |
| fact_instalment[instalments] | Whole number, Summarization: Don't summarize | It is a count per payment; adding it up means nothing |
| fact_instalment[amount] | Fixed decimal number, `#,0.00` | Money to the cent (already set in Power Query) |

## Display folders

Each measure in `03-measures.dax` names its folder (Cash, Late, Dates). Select the measure in Model view > Properties > Display folder.
Why: the 12 measures stay findable in the Data pane, grouped by the question they answer.
