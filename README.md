<p align="center">
  <img width="100%" src="docs/header.svg" alt="Daily cash and payments. 103,886 payments: 76% of the cash in arrived by credit card, and BRL 1.56 million was still due on instalments.">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL 17">
  <img src="https://img.shields.io/badge/SQL-Star_schema-0E1630?style=for-the-badge" alt="SQL star schema">
  <img src="https://img.shields.io/badge/Power_BI-DAX_%26_Power_Query-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" alt="Power BI, DAX and Power Query">
  <img src="https://img.shields.io/badge/Python-pandas-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python and pandas">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Compose">
</p>

## The problem

The owner learns how much cash came in only at month end, from a spreadsheet nobody trusts. Card payments arrive in instalments over many months, boleto payments arrive when the customer gets round to paying, and nobody can say on a given day what has come in, what is still owed, or which payments are late.

## 🛠️ The solution

A small warehouse in PostgreSQL that turns every order and payment into one row per instalment, with the cash rules written once in SQL, and a Power BI report on top of it: a daily cash page and a due-and-late page. One command loads it and proves that every total still matches the source.

<p align="center">
  <img width="100%" src="docs/how-it-works.svg" alt="How it works: 01 Load, orders, payments and customers; 02 Rules, cash in, still due, late and never paid defined once; 03 Model, a star schema with a date table; 04 Report, a Power BI daily cash page.">
</p>

### 🔁 The mental model: where the money goes

Every payment flows from how it was paid to where it stands on the report date. Card instalments are what push money into the months ahead.

<p align="center">
  <img width="100%" src="docs/mental-model.svg" alt="Where the money goes: BRL 16.0 million across 103,886 payments, by payment method, into received (BRL 14.4 million), still due on card instalments (BRL 1.56 million) and never paid (BRL 37 thousand).">
</p>

### 📏 The rules, written once

All four live in [`sql/2_rules.sql`](sql/2_rules.sql). The notebook and every Power BI measure read them; nothing redefines them.

1. **Cash date.** The source records how many instalments a card payment has, but not when each one is paid. So this is an assumption, not data: instalment 1 is counted on the day the payment was confirmed, instalment *k* is counted *k* − 1 months later. Boleto, debit card and voucher are one instalment.
2. **Report date.** The last day any payment was confirmed: 3 Sep 2018. Instalments on or before it are *received*; later ones are *still due*.
3. **Late.** A payment confirmed more than 3 days after the order was placed (`rules.late_after_days` in [`config/client.yaml`](config/client.yaml)).
4. **Never paid.** An order whose payment was never confirmed.

The instalments of a payment add up to its value to the cent (the first ones are cut to the cent, the last takes the remainder), so the model can be reconciled exactly.

## 📈 The result

**103,886 payments: 76% of the cash in arrived by credit card, and BRL 1.56 million was still due on instalments.**

| Question | Answer |
|---|---|
| How much was paid? | BRL 16,008,872.12 across 103,886 payments, matching the source to the cent |
| How much came in? | BRL 14,415,391.61 (90.0%) by the report date |
| How much is still due? | BRL 1,556,350.74 (9.7%) on 11,648 card payments, the last instalment in May 2020 |
| How does it arrive? | Credit card 76.1% of the cash in, boleto 19.9%, voucher 2.5%, debit card 1.5% |
| From where? | The Southeast brings in 64.8%; the South 14.5%, the Northeast 11.7% |
| What is late? | 2,301 payments (2.2% of those confirmed), BRL 353,690.84; 78% of them are boleto, and 9.1% of boleto payments are late against 0.6% of card payments |
| What was never paid? | BRL 37,129.77 on 175 payments |

![Cash by month: received, then card instalments still to come](docs/cash-by-month.png)

![Share of the cash in by payment method and by region](docs/where-the-money-comes-from.png)

![Share of payments confirmed late, by payment method](docs/late-payments.png)

Every number above is computed in [`analysis/analysis.ipynb`](analysis/analysis.ipynb), saved with its outputs, and checked with SQL in [`powerbi/06-checks.md`](powerbi/06-checks.md).

## 📊 The Power BI report

Two pages on the star schema: **Daily cash** (cash in by day, payment method and region, with payments confirmed and the late rate for any date range) and **Due and late** (instalments still due by month, money never paid, and every late payment listed).

The report is built step by step from [`powerbi/`](powerbi/): every Power Query step, the model, every DAX measure, each visual with its fields, the theme, and the numbers each card must show.

## 🏗️ How it is built

- **Load** ([`sql/1_load.sql`](sql/1_load.sql), [`load.py`](load.py)): the five input files in [`data/input/`](data/input/README.md) (orders, payments, customers, and the payment-method and region mapping files) are checked for their columns, then go into `raw` tables as they are, with `COPY`. Every client value (names, currency, the late threshold, colours, file names) comes from [`config/client.yaml`](config/client.yaml) through [`config.py`](config.py).
- **Rules** ([`sql/2_rules.sql`](sql/2_rules.sql)): one row per instalment, with its cash date, amount, status (Received, Due or Never paid) and late flag.
- **Model** ([`sql/3_model.sql`](sql/3_model.sql)): a star schema around `mart.fact_instalment` (296,425 rows) with `dim_date` (every day from the first order to the last instalment), `dim_payment_method` and `dim_state` (state and region). The keys are the natural codes, enforced with primary and foreign keys, so a fact row that points at a missing day, method or state fails the load.
- **Check:** `load.py` ends by proving that the model holds all 103,886 source payments and that received + still due + never paid equals the source total to the cent; it stops with an error if not.
- **Numbers:** [`analysis/analysis.ipynb`](analysis/analysis.ipynb) reads the model with pandas, re-reads the raw payments file without the database for an independent total, and draws the charts.

## ▶️ Run it

You need Docker, Python 3.10 or later, and the three data files (see Data).

```bash
cp .env.example .env
docker compose up -d
pip install -r requirements.txt
python load.py
python theme.py
python -m nbconvert --to notebook --execute --inplace analysis/analysis.ipynb
```

`load.py` rebuilds everything from scratch each time and ends with `check passed`. The database listens on `127.0.0.1:5434` (database and user `cash`; the password is in `.env`). `theme.py` writes the Power BI theme from the colours in `config/client.yaml`.

## ⚠️ Limits

The instalment schedule is a stated assumption (rule 1), so "cash by day" for card payments after instalment 1 is modelled, not observed. "Late" only sees the gap between order and payment confirmation; the source has no due dates for individual instalments, so a missed instalment cannot be seen. Amounts are what customers paid, freight included.

## 🗂️ Data

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) on Kaggle (CC BY-NC-SA 4.0): about 100,000 orders placed from 2016 to 2018, with payments by method and number of instalments, and customers by state. This project uses three of its files. Download them from Kaggle and put them in `data/input/` (they are not committed):

- `olist_orders_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_customers_dataset.csv`

The state list in [`data/input/regions.csv`](data/input/regions.csv) derives from the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (CC BY-NC-SA 4.0); a client's private copy replaces it with their own mapping.

---

Built by [Omar Shalaby](https://github.com/omarshalabyy1) · PostgreSQL, SQL, Python, Power BI, DAX, Power Query
