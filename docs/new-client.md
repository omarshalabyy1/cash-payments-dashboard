# New client

This repo is a GitHub template. A new client gets a **private** repo from it (Use this template > Create a new repository > Private); client data never goes into this public repo.
Everything that changes per client is in three places: `config/client.yaml`, `.env`, and the files in `data/input/`.

## Done in the template

What the client gets with no work. Hours are an estimate of building each part from scratch.

| Part | Estimate (hours) |
|---|---|
| PostgreSQL warehouse in Docker; input files checked for their columns, then loaded with `COPY` (`load.py`, `sql/1_load.sql`) | 3 |
| Cash rules in SQL: instalments split to the cent, received, still due, late, never paid; the reconciliation check to the cent (`sql/2_rules.sql`, `load.py`) | 5 |
| Star schema with a date table and enforced keys (`sql/3_model.sql`) | 2 |
| Client settings: `config/client.yaml`, `config.py` (`load_config()`), `.env`, the Power BI theme written from the config (`theme.py`) | 2 |
| Analysis notebook: every number, three charts, the Power BI check numbers, the result sentences (`analysis/analysis.ipynb`) | 4 |
| Power BI build pack: 5 queries, the model, 12 measures, 2 pages with 22 visuals, interactions, checks C1 to C8, a 32-step checklist (`powerbi/`) | 8 |
| README with its diagrams, and the input file guide (`data/input/README.md`) | 3 |
| **Total** | **27** |

## Configure

Per client, file by file. Hours are an estimate.

| File | Key | Example | Estimate (hours) |
|---|---|---|---|
| `config/client.yaml` | `client.name`, `client.currency`, `client.decimals`, `report.title`, `report.colours` | `EGP`, `2`, `"#0F766E"` | 0.5 |
| `.env` | `DB_PASSWORD` | a new password | 0.25 |
| `data/input/` orders, payments, customers | `inputs.orders`, `inputs.payments`, `inputs.customers` | `orders.csv` with `order_approved_at` | 3 |
| `data/input/` mapping files | `inputs.payment_methods`, `inputs.regions` | `fawry,Fawry,3` | 1 |
| `config/client.yaml` | `rules.late_after_days`, `report.check_month` | `2`, `"2025-03"` | 0.25 |
| Run `load.py`, `theme.py` and the notebook; fix what the checks report | | | 1 |
| Power BI: build from `powerbi/08-build-checklist.md` with the client's server in the Warehouse query; copy the notebook's section 5 into `powerbi/06-checks.md` | `warehouse.*` | `127.0.0.1:5434` | 2 |
| **Total** | | | **8** |

## Custom

Typical work for one client beyond the template. Hours are an estimate.

| Work | Estimate (hours) |
|---|---|
| The client's real payout dates (card settlement or instalment due dates) in place of rule 1's monthly schedule | 4 |
| One more page or measure set, for example refunds and chargebacks | 4 |
| Scheduled refresh: a daily Airflow run or a Power BI gateway | 3 |
| **Total** | **11** |

## Share already done (estimate)

Template hours ÷ (template + configure + custom) hours = 27 ÷ (27 + 8 + 11) = 27 ÷ 46 = **59%** (58.7%).

## Steps

1. Create the private repo from the template and clone it.
2. `cp .env.example .env` and set `DB_PASSWORD`.
3. Edit `config/client.yaml`.
4. Put the five files in `data/input/` ([columns and examples](../data/input/README.md)).
5. `docker compose up -d`, `python load.py`, `python theme.py`, then run the notebook.
6. Build the Power BI report from `powerbi/`.

## Second-client drill (2026-10-05)

The acceptance test of the template: a copy of the repo, a made-up second client, a run from scratch.

**Client B (drill):** currency `EGP`, `late_after_days: 2`, teal colours (`#0F766E` main), title "Client B cash", check month `2025-03`. Input: 5 orders, 6 payments, 4 customers; three-letter region codes (`CAI`, `GIZ`, `ALX`); an extra column in orders and in customers; one order paid two ways; one order never paid; one payment confirmed 3 days after its order.

| What | Demo (Olist) | Client B (drill) |
|---|---|---|
| Load check | passed: BRL 16,008,872.12 = 14,415,391.61 + 1,556,350.74 + 37,129.77 | passed: EGP 2,410.50 = 1,550.50 + 800.00 + 60.00 |
| Payments | 103,886 | 6 |
| Report date | 3 Sep 2018 | 5 Apr 2025 |
| Late (threshold) | 2,301 of 103,711 confirmed, 2.2% (3 days) | 1 of 5 confirmed, 20.0% (2 days) |
| Top method share of cash in | credit card 76% | card 76% |
| Top region | Southeast 65% | Greater Cairo 87% |
| Check month | May 2018: cash in 1,117,998.16, 7,334 confirmed, 99 late | Mar 2025: cash in 750.50, 3 confirmed, 1 late |
| Power BI theme | "Daily cash and payments", `#2563EB` | "Client B cash", `#0F766E`, page `#F0FDFA` |
| Notebook | 0 errors | 0 errors; chart titles name Client B, amounts in EGP |

Every Client B number matches a hand calculation from its six payments.

**Clear failures**, one line each, run on the Client B copy:

```
config/client.yaml is missing rules.late_after_days
.env is missing DB_PASSWORD (copy .env.example to .env)
missing input file data/input/customers.csv (inputs.customers in config/client.yaml)
data/input/payments.csv is missing column(s): payment_value
Key (payment_type)=(fawry) is not present in table "dim_payment_method".
```

**Nothing hard-coded:** this search over the code (`*.py`, `sql/*.sql`, `powerbi/03-measures.dax`, `docker-compose.yml`), the Power Query M code and the notebook's source cells finds nothing:

```
BRL|Sample online store|#[0-9A-Fa-f]{6}|3 days|olist_|Southeast|Boleto|boleto|Credit card|2018-05
```

The README, the diagrams in `docs/` and the numbers in `powerbi/06-checks.md` describe the demo run, so they keep its values on purpose.

**Nothing broke:** after the drill, `python load.py` on the demo data passed again with the same totals.
