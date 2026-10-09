# The project explained, from zero

This page explains the whole project in plain words: what it does, what every word means, where every number comes from, and how to talk about it in an interview. You do not need to know SQL or Power BI to read it.

[← Back to the README](../README.md)

## 1. The project in one minute

An online shop sells things. Customers pay in different ways: by credit card, by **boleto** (a Brazilian bank slip the customer pays at a bank or online), by debit card or with a voucher. A credit card payment can be split into monthly **instalments**: a 1,200 purchase in 12 instalments brings in 100 a month for a year.

So the owner cannot answer simple questions on a given day:

- How much money has actually come in?
- How much is still on its way from instalments?
- Which payments came in late, and which were never paid?

This project answers them. It loads the shop's orders and payments into a database, splits every payment into its instalments, gives every instalment a date and a status, and puts a Power BI report on top. A check at the end proves that no money was lost or counted twice.

Think of it like a jar for each month: every payment drops its instalments into the right monthly jars. Jars on or before today are money **received**. Jars after today are money **still due**.

## 2. Words you will meet

| Word | What it means here |
|---|---|
| **BRL** | Brazilian real, the currency of the data. "BRL 1.56M" means 1.56 million reais. |
| **Boleto** | A Brazilian bank slip. The customer gets a slip and pays it later, so the money can arrive days after the order. |
| **Voucher** | A gift card or store credit used to pay. |
| **Instalment** | One part of a payment that is split over months. A payment in 8 instalments has 8 parts. |
| **Report date** | "Today" for the report: the last day any payment was confirmed in the data, 3 Sep 2018. |
| **Received / Still due / Never paid** | The three statuses an instalment can have. See section 4. |
| **Late** | A payment confirmed more than 3 days after the order was placed. |
| **Database** | A program that stores tables and answers questions about them. This project uses **PostgreSQL** (often "Postgres"), a free and widely used one. |
| **SQL** | The language used to ask a database questions and build tables. The `.sql` files in `sql/` are SQL. |
| **Table, row, column** | Like a spreadsheet sheet: each row is one thing (one order, one payment), each column is one fact about it (its date, its amount). |
| **Schema** | A folder of tables inside the database. This project has one per layer: `bronze`, `silver`, `gold`, `semantic` and `analytical`, plus `ops` for the load log. |
| **Layers** | The six steps the data goes through, left to right, each reading only the one before it. **Bronze**: the files as they came, as text, with the file and row each value came from. **Silver**: the same rows with types and keys. **Gold**: the business rules. **Semantic**: the star schema the report reads. **Analytical**: totals over the star schema. **Reporting**: the notebook and Power BI. |
| **Quarantine** | `bronze.quarantine`, where a row the load refuses goes (an empty required value, or a value that is not a valid number or date), with the reason. 0 rows in this data. |
| **Warehouse** | A database built for reporting, not for running the shop. Here, the PostgreSQL database with the six layers' schemas. |
| **CSV** | A plain text file of a table, one row per line, values separated by commas. The inputs are CSV files. |
| **`COPY`** | The PostgreSQL command that loads a whole CSV file into a table at once. Much faster than inserting rows one by one. |
| **Fact table** | The big table of events you add up. Here `fact_instalment`: one row per instalment, with its amount. |
| **Dimension table** | A small lookup table that describes the facts: the dates (`dim_date`), the payment methods (`dim_payment_method`), the states (`dim_state`). You filter and group by them. |
| **Star schema** | One fact table in the middle with dimension tables around it, like a star. It is the standard shape for Power BI reports. See [data-model.svg](data-model.svg). |
| **Grain** | What one row of a table stands for. The grain of `fact_instalment` is "one instalment of one payment". |
| **Primary key (PK)** | The column (or columns) that makes each row unique. Two rows can never share it. |
| **Foreign key (FK)** | A column that must point to an existing row in another table. If a payment uses a method that is not in `dim_payment_method`, the load stops. |
| **Natural key** | A key that already exists in the data (a date, the state code "SP"). The opposite is a **surrogate key**, a made-up number like 1, 2, 3. |
| **Date table** | A dimension with one row per day, so every day exists even if nothing happened on it. Power BI needs one to group by month and year. |
| **Reconcile** | To prove two totals match. Here: the money in the model equals the money in the source file, to the cent. |
| **Python, pandas** | Python is a programming language. pandas is its library for tables. `load.py` and the notebook use them. |
| **Notebook** | `analysis/analysis.ipynb`, a file that mixes code, its output and notes. It computes every number in the README. |
| **Docker, Docker Compose** | Docker runs programs in a ready-made box called a container, so nobody installs PostgreSQL by hand. `docker-compose.yml` says which boxes to start. |
| **Port 5434** | The "door number" the database listens on. Each portfolio project uses its own number so several can run at once. |
| **`.env`** | A file for secrets, like the database password. It is never committed; `.env.example` shows its shape. |
| **`config/client.yaml`** | The settings a client would change: shop name, currency, file names, the late threshold, colours. YAML is a simple text format for settings. |
| **Power BI** | Microsoft's tool for interactive reports and dashboards. |
| **Power Query** | The part of Power BI that loads and shapes data before the report uses it. |
| **DAX** | The formula language of Power BI, used to write **measures** (calculations like "Cash In" or "Late Rate %"). |
| **Theme** | A Power BI file that sets the report's colours and fonts. `theme.py` writes it from `client.yaml`. |

## 3. How it works, file by file

Run in this order (the commands are in the README's "Run it" section):

| Step | File | What it does |
|---|---|---|
| 0 | `docker-compose.yml` | Starts PostgreSQL in a container on port 5434. |
| 0 | `config/client.yaml`, `config.py` | Hold every setting; `config.py` reads them so no file hard-codes a value. |
| 1 | `load.py` | Bronze layer. Checks that the 5 input files exist, have the needed columns and have rows, then loads each into a `bronze` table with `COPY`, as text, unchanged, with the file name, row number, run id and load time. A row with an empty required value or a value that is not a valid number or date goes to `bronze.quarantine`; a key that appears twice stops the load. Each load is logged in `ops.load_log`. |
| 2 | `sql/2_silver.sql` | Silver layer. Gives every column its type (dates, whole numbers, money) and its primary key. `load.py` then checks that no row was lost on the way. |
| 3 | `sql/3_gold.sql` | Gold layer, the business rules. Splits each payment into instalments, gives each a cash date, an amount, a status and a late flag. Builds `gold.instalment`. |
| 4 | `sql/4_semantic.sql` | Semantic layer. Copies the instalments into `semantic.fact_instalment`, builds the three dimension tables (the dates from the calendar setting, the methods and states from Silver) and adds the primary and foreign keys. This makes the star schema. |
| 5 | `sql/5_analytical.sql` | Analytical layer. Three views of totals over the star schema: by payment method, by region and by month. |
| 6 | end of `load.py` | The check: every payment loaded is in the star schema, and received + still due + never paid = the source total. If not, it stops with `CHECK FAILED`, and nothing is changed: the whole run is one transaction. |
| 7 | `theme.py` | Writes the Power BI theme file from the colours in `client.yaml`. |
| 8 | `analysis/analysis.ipynb` | Reporting layer. Reads the Semantic and Analytical layers, computes every number in the README and draws the charts in `docs/`. |
| 9 | `powerbi/` | Reporting layer. Step-by-step instructions to build the Power BI report: queries, model, measures, pages, and the numbers each card must show (`06-checks.md`). |

The 5 input files: 3 come from the shop (orders, payments, customers; you download them, see Data in the README) and 2 are small mapping files committed in `data/input/` (`payment_methods.csv` gives each payment code a readable name, `regions.csv` gives each state its name and region).

### The rules, with an example

One real payment from the data (order `b81ef226…`): BRL 99.33 paid by credit card in 8 instalments. The order was placed on 25 Apr 2018 at 22:01 and the payment was confirmed at 22:15 the same evening.

1. **Split.** 99.33 / 8 = 12.41625. The first 7 instalments are cut (not rounded) to the cent: 12.41 each, 86.87 in total. The last one takes what is left: 99.33 − 86.87 = 12.46. So the 8 parts add up to exactly 99.33. Rounding each part would lose or add a cent here and there, and the totals would stop matching the source.
2. **Cash date.** Instalment 1 lands on the day the payment was confirmed (25 Apr 2018). Instalment 2 one month later (25 May 2018), and so on to instalment 8 (25 Nov 2018). The data says how many instalments there are, but not when each was paid, so this monthly schedule is an assumption. The README says so in "Limits".
3. **Status.** The report date is 3 Sep 2018. Instalments 1 to 5 (April to August) fall on or before it, so they are **Received**: 5 × 12.41 = 62.05. Instalments 6 to 8 (September to November) fall after it, so they are **Still due**: 12.41 + 12.41 + 12.46 = 37.28. 62.05 + 37.28 = 99.33. A payment that was never confirmed has no cash date and is **Never paid**.
4. **Late.** The payment was confirmed 14 minutes after the order, so it is not late. Late means confirmed more than 3 days after the order.

## 4. Every number, explained

All of these are printed by the notebook ([`analysis/analysis.ipynb`](../analysis/analysis.ipynb)). The cell numbers below count from 0, the first cell.

### The headline and the results table

| Number | What it means | How it is worked out | Where |
|---|---|---|---|
| **103,886 payments** | Every payment in the source file. One order paid two ways counts as two payments. | Count of rows in the payments file. The model holds the same count. | notebook cell 3; `load.py` check |
| **BRL 16,008,872.12** | All the money customers paid, in total. | Sum of `payment_value` in the source file, and again in the model: both give the same number to the cent. | notebook cell 3 |
| **BRL 14,415,391.61 (90.0%)** | Money that had come in by the report date. | Sum of all instalments with status Received. 14,415,391.61 / 16,008,872.12 = 90.0%. | notebook cell 5 |
| **BRL 1,556,350.74 (9.7%)** | Money still to come from card instalments after the report date. | Sum of instalments with status Due. Shown in the header as "BRL 1.56 million". | notebook cell 5 |
| **11,648 card payments** | Payments that still have at least one instalment to come. | Count of distinct payments with a Due instalment. | notebook cell 5 |
| **May 2020** | When the very last instalment falls due (3 May 2020). | The latest cash date among Due instalments: a payment confirmed near the end of the data, split into up to 24 monthly parts. | notebook cell 5 |
| **BRL 37,129.77 on 175 payments** | Money that was never paid: the payment was never confirmed. | Sum and count of instalments with status Never paid. | notebook cell 5 |
| **76.1% by credit card** | Of the money received, the share paid by credit card. | 10,975,162.62 / 14,415,391.61. Boleto 19.9%, voucher 2.5%, debit card 1.5% are worked out the same way. | notebook cell 8 |
| **Southeast 64.8%** | Of the money received, the share from customers in the Southeast region of Brazil. | 9,342,516.46 / 14,415,391.61. South 14.5%, Northeast 11.7% the same way (Central-West 6.4%, North 2.6% are in the notebook). | notebook cell 8 |
| **2,301 late payments (2.2%)** | Payments confirmed more than 3 days after the order. | 2,301 late / 103,711 confirmed payments = 2.2%. Payments never paid are left out: a payment that never arrived cannot arrive late. | notebook cell 11 |
| **BRL 353,690.84** | The value of those late payments. | Sum of every instalment of every late payment. | notebook cell 11 |
| **78% of late are boleto** | Most late payments were bank slips. | 1,796 late boleto payments / 2,301 late payments. | notebook cell 11 |
| **9.1% of boleto vs 0.6% of card** | How often each method is late. | Boleto: 1,796 late / 19,754 confirmed. Card: 429 late / 76,739 confirmed. | notebook cell 11 |
| **3 Sep 2018** | The report date ("today"). | The last day any payment was confirmed in the data. | `sql/3_gold.sql`; notebook cell 1 |
| **3 days** | The late threshold. | A setting, `rules.late_after_days` in `config/client.yaml`. A client can change it. | `config/client.yaml` |

Two things that can look wrong but are not:

- **90.0% + 9.7% + 0.2% = 99.9%, not 100%.** Each share is rounded to one decimal. The exact amounts add up to the total to the cent.
- **Payments per status add up to more than 103,886** (103,711 + 11,648 + 175). A card payment with some instalments received and some still due is counted in both. Every payment has its first instalment either Received (103,711) or Never paid (175), and 103,711 + 175 = 103,886.

### The diagrams

| Number | Where you see it | What it means |
|---|---|---|
| **5 CSV files** | data-flow.svg | The 5 input files (3 from the shop, 2 mapping files). |
| **99,441** | data-flow.svg | Rows in `bronze.orders` and `bronze.customers` (and the same in Silver): one customer row per order in this data. |
| **0 rows refused** | data-flow.svg | Rows in `bronze.quarantine`: every row of the 5 files was loaded. |
| **296,425** | data-flow.svg, data-model.svg | Rows in `fact_instalment`. It is more than 103,886 because each payment becomes one row per instalment: adding up the number of instalments of every payment gives 296,425 (a payment marked with 0 instalments counts as 1). |
| **1,827 rows** | data-model.svg | Days in `dim_date`: every day of the years 2016 to 2020, the fixed range `calendar.start` to `calendar.end` in `config/client.yaml`. It covers the first order (4 Sep 2016) and the last instalment (3 May 2020). |
| **44 rows** | data-flow.svg | Months in `analytical.cash_by_month`: every month with money received or still due. |
| **5 rows** | data-model.svg | Payment methods in `dim_payment_method`: credit card, boleto, voucher, debit card and "not defined" (3 payments of 0.00 in the source). |
| **27 rows** | data-model.svg | Brazil's 26 states plus the Federal District, in `dim_state`. |
| **1 to \*** | data-model.svg | One dimension row links to many fact rows: one day has many instalments. |
| **51,338 of 76,795 in 2 to 24 instalments** | mental-model.svg | 76,795 credit card payments; 51,338 of them were split into 2 or more instalments, up to 24. |
| **BRL 12.5M, 2.87M, 379k, 218k** | mental-model.svg | Total paid by credit card, boleto, voucher and debit card (all statuses, so slightly more than the received shares above). |
| **1 to 6** | how-it-works.svg | The six layers: Bronze, Silver, Gold, Semantic, Analytical, Reporting. |
| **Jan 2017 to Jun 2019** | header.svg | The months shown in the small header chart. The full chart in the README runs to May 2020. |

## 5. What the results mean for the business

- **Most of the cash is safe and in.** 90% of all money paid had arrived by the report date. The owner can see that on any day, not only at month end.
- **Card instalments are future cash, not cash today.** BRL 1.56 million was still to come, spread over the months up to May 2020. That is money the shop can plan with, but cannot spend yet.
- **Late payments are a boleto problem.** 9.1% of boleto payments were late against 0.6% of card payments, and boleto made up 78% of all late payments. If speed of cash matters, the shop could nudge customers towards card or send boleto reminders.
- **Very little money is lost.** Only BRL 37 thousand (0.2%) was never paid.
- **The Southeast region brings in about two thirds of the cash.** Any change there moves the whole business.

## 6. Interview questions you can expect

**Explain the project in 30 seconds.**
A shop could not see its cash on a given day because card payments arrive in instalments and bank-slip payments arrive late. I loaded orders and payments into PostgreSQL, split each payment into its instalments with a cash date and a status, built a star schema and a Power BI report on it, and added a check that proves every total matches the source to the cent. Result: BRL 14.4 million received, BRL 1.56 million still due, and boleto behind 78% of late payments.

**Why one row per instalment?**
Because cash arrives per instalment, not per payment. With one row per instalment, "cash in by month" is a simple sum by cash date. With one row per payment, every report would have to split the payment again, in DAX, every time.

**How do you know the numbers are right?**
Four ways. A row that is not valid is never loaded quietly: it goes to `bronze.quarantine` with the reason, and `ops.load_log` keeps the rows in each file, loaded and refused. `load.py` checks that the model holds all 103,886 payments and that received + due + never paid equals the source total, and stops if not. The notebook re-reads the payments file with pandas, without the database, and asserts the same totals. And the foreign keys stop the load if a payment points at a method, state or day that does not exist.

**Why split amounts by cutting to the cent and giving the remainder to the last instalment?**
So the parts always add back to the original amount. Rounding each part can create or lose a cent, and then the reconciliation fails.

**The cash date is an assumption. How would you handle it with real data?**
I would load the real settlement file from the card company, which says when each instalment was actually paid, and use that date instead of "one month later". The rule lives in one SQL file, so only that file changes.

**Why natural keys and not surrogate keys?**
The keys here (a date, a payment code, a state code) never change, and a surrogate key would only add a lookup. If a key could change, for example a product code that gets renamed, I would use a surrogate key.

**Why are the rules in SQL and not in DAX?**
So they are written once and every tool reads the same answer: the notebook, the check and every Power BI measure read the status and late flag from the table. Nothing redefines them.

**Why does the load rebuild everything each time?**
The data is small (about 300 thousand rows), so a full rebuild takes seconds and can never leave half-updated tables. With millions of new rows a day I would load only new rows (an incremental load).

**How would you set it up for a real client?**
Change `config/client.yaml` (name, currency, file names, late threshold, colours), put their 5 files in `data/input/`, and run the same commands. No code changes.

## 7. Limits, in plain words

- The monthly instalment schedule is an assumption, because the data does not say when each instalment was really paid.
- "Late" only measures the time from order to payment confirmation. The data has no due date per instalment, so a missed instalment cannot be seen.
- Amounts are what customers paid, including delivery fees.
