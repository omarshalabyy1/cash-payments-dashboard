# 06 · Checks

Every number below comes from `analysis/analysis.ipynb` (section 5) and is checked by the SQL query under it.
If a card shows anything else, the build has a mistake; the usual causes are at the bottom.

Run a query from the repo folder, with the warehouse up:

```bash
docker compose exec db psql -U cash -d cash -c "<paste the query here>"
```

## Page 1 · Daily cash

| Visual | No slicer selected | Date slicer 1 May to 31 May 2018 |
|---|---|---|
| Cash in | 14.42M (14,415,391.61) | 1.12M (1,117,998.16) |
| Payments confirmed | 103,711 | 7,334 |
| Late payments | 2,301 | 99 |
| Late rate | 2.2% | 1.3% |
| Report date | 3 Sep 2018 | 3 Sep 2018 |

```sql
select sum(amount) filter (where status = 'Received') as cash_in,
       count(*) filter (where instalment_no = 1 and status = 'Received') as payments_confirmed,
       count(*) filter (where instalment_no = 1 and status = 'Received' and is_late) as late_payments,
       round(100.0 * count(*) filter (where instalment_no = 1 and status = 'Received' and is_late)
             / count(*) filter (where instalment_no = 1 and status = 'Received'), 1) as late_rate_pct
from mart.fact_instalment;
-- for May 2018, add before the semicolon: where cash_date between '2018-05-01' and '2018-05-31'
```

**Cash in by payment method** (no slicer; tooltip = share):

| Payment method | Cash in | Share |
|---|---|---|
| Credit card | 10,975,162.62 | 76.1% |
| Boleto (bank slip) | 2,865,633.94 | 19.9% |
| Voucher | 356,605.26 | 2.5% |
| Debit card | 217,989.79 | 1.5% |

```sql
select m.payment_method, sum(f.amount) as cash_in,
       round(100.0 * sum(f.amount) / sum(sum(f.amount)) over (), 1) as share_pct
from mart.fact_instalment f join mart.dim_payment_method m using (payment_type)
where f.status = 'Received' group by m.payment_method order by cash_in desc;
```

**Cash in by region** (no slicer; tooltip = share):

| Region | Cash in | Share |
|---|---|---|
| Southeast | 9,342,516.46 | 64.8% |
| South | 2,085,427.96 | 14.5% |
| Northeast | 1,686,567.07 | 11.7% |
| Central-West | 922,523.27 | 6.4% |
| North | 378,356.85 | 2.6% |

```sql
select s.region, sum(f.amount) as cash_in,
       round(100.0 * sum(f.amount) / sum(sum(f.amount)) over (), 1) as share_pct
from mart.fact_instalment f join mart.dim_state s using (customer_state)
where f.status = 'Received' group by s.region order by cash_in desc;
```

## Page 2 · Due and late

| Visual | No slicer selected |
|---|---|
| Still due on instalments | 1.56M (1,556,350.74) |
| Never paid | 37.1K (37,129.77) |
| Money in late payments | 353.7K (353,690.84) |
| Late payments table: Amount total | 353,690.84 |

```sql
select sum(amount) filter (where status = 'Due') as still_due,
       sum(amount) filter (where status = 'Never paid') as never_paid,
       sum(amount) filter (where is_late) as late_amount,
       max(cash_date) filter (where status = 'Received') as report_date
from mart.fact_instalment;
```

**Still due by month**, the first four columns:

| Month | Still due |
|---|---|
| 2018-09 | 451,045.10 |
| 2018-10 | 358,412.19 |
| 2018-11 | 252,853.90 |
| 2018-12 | 180,381.17 |

```sql
select to_char(cash_date, 'YYYY-MM') as year_month, sum(amount) as still_due
from mart.fact_instalment where status = 'Due' group by 1 order by 1 limit 4;
```

**Late payments by method** (matrix):

| Payment method | Payments confirmed | Late payments | Late rate | Late amount |
|---|---|---|---|---|
| Credit card | 76,739 | 429 | 0.6% | 88,672.94 |
| Boleto (bank slip) | 19,754 | 1,796 | 9.1% | 258,740.57 |
| Voucher | 5,689 | 47 | 0.8% | 3,093.70 |
| Debit card | 1,529 | 29 | 1.9% | 3,183.63 |
| Total | 103,711 | 2,301 | 2.2% | 353,690.84 |

```sql
select m.payment_method,
       count(*) filter (where f.instalment_no = 1 and f.status = 'Received') as payments_confirmed,
       count(*) filter (where f.instalment_no = 1 and f.status = 'Received' and f.is_late) as late_payments,
       sum(f.amount) filter (where f.is_late) as late_amount
from mart.fact_instalment f join mart.dim_payment_method m using (payment_type)
group by m.payment_method, m.sort_order order by m.sort_order;
```

## If a number is off

- **Cash in or Still due too high or too low:** `amount` is not Fixed decimal number, or a status filter in a measure has a typo ("Received", "Due", "Never paid" are case sensitive in the data).
- **Payments confirmed counts every instalment:** the `instalment_no = 1` filter is missing from the measure.
- **Dates split into Year, Quarter, Month:** Auto date/time is still on (see `README.md`, before you start).
- **The May 2018 numbers do not change with the slicer:** the relationship `dim_date[date]` → `fact_instalment[cash_date]` is missing or inactive.
- **Shares do not add up to 100%:** the tooltip uses `[Share of Cash In %]`, not a quick measure.
