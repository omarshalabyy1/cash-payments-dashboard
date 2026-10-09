-- Analytical layer: the totals the README, the notebook and powerbi/06-checks.md quote, as views over the
-- Semantic layer only. No rule here: status and is_late come from the Gold layer through semantic.fact_instalment.

drop schema if exists analytical cascade;
create schema analytical;

-- One row per payment method that has a payment. cash_in is empty for a method with nothing received.
-- A confirmed payment is counted once, on its first instalment.
create view analytical.cash_by_method as
select
    m.payment_method,
    m.sort_order,
    sum(f.amount)                                                                    as total_paid,
    sum(f.amount) filter (where f.status = 'Received')                               as cash_in,
    count(*) filter (where f.instalment_no = 1 and f.status = 'Received')            as payments_confirmed,
    count(*) filter (where f.instalment_no = 1 and f.status = 'Received' and f.is_late) as late_payments,
    sum(f.amount) filter (where f.is_late)                                           as late_amount
from semantic.fact_instalment f
join semantic.dim_payment_method m using (payment_type)
group by m.payment_method, m.sort_order;

-- One row per region with money received.
create view analytical.cash_in_by_region as
select s.region, sum(f.amount) as cash_in
from semantic.fact_instalment f
join semantic.dim_state s using (customer_state)
where f.status = 'Received'
group by s.region;

-- One row per month of cash date: money received and money still due on instalments.
-- Never paid has no cash date, so it is in no month.
create view analytical.cash_by_month as
select
    d.year_month,
    coalesce(sum(f.amount) filter (where f.status = 'Received'), 0) as received,
    coalesce(sum(f.amount) filter (where f.status = 'Due'), 0)      as still_due
from semantic.fact_instalment f
join semantic.dim_date d on d.date = f.cash_date
group by d.year_month;
