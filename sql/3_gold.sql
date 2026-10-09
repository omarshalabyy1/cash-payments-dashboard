-- Gold layer: the cash rules, defined once. One row per instalment of a payment, with its cash date, amount,
-- status and late flag. The Semantic layer, the notebook and every Power BI measure read them; nothing redefines them.
--
-- The source says how many instalments a card payment has, but not when each one is paid. So the
-- schedule below is a stated assumption, not data:
--   1. Cash date: instalment 1 is counted on the day the payment was confirmed (order_approved_at);
--      instalment k is counted k - 1 months later. A payment in one instalment lands on that first day.
--   2. Report date: the last day any payment was confirmed. Instalments on or before it are Received;
--      later ones are Due.
--   3. Late: a payment confirmed more than rules.late_after_days (config/client.yaml) days after the order
--      was placed. load.py passes the number in as the setting client.late_after_days.
--   4. Never paid: an order whose payment was never confirmed. It has no cash date.
-- The instalments of a payment add up to its value to the cent: the first N - 1 are cut to the cent,
-- the last one takes the remainder.

drop schema if exists gold cascade;
create schema gold;

create table gold.instalment as
with payment as (
    select
        p.order_id || '-' || p.payment_sequential as payment_id,
        p.order_id,
        p.payment_type,
        greatest(p.payment_installments, 1)       as instalments,   -- 0 is read as 1: a payment is at least one instalment
        p.payment_value,
        c.customer_state,
        o.order_purchase_timestamp::date          as order_date,
        o.order_approved_at,
        o.order_approved_at > o.order_purchase_timestamp
            + make_interval(days => current_setting('client.late_after_days')::int) as confirmed_late
    from silver.order_payments p
    join silver.orders o    on o.order_id = p.order_id
    join silver.customers c on c.customer_id = o.customer_id
),
instalment as (
    select
        p.*,
        n.instalment_no,
        (p.order_approved_at + (n.instalment_no - 1) * interval '1 month')::date as cash_date,
        case when n.instalment_no < p.instalments
             then trunc(p.payment_value / p.instalments, 2)
             else p.payment_value - (p.instalments - 1) * trunc(p.payment_value / p.instalments, 2)
        end as amount
    from payment p
    cross join lateral generate_series(1, p.instalments) as n(instalment_no)
)
select
    i.payment_id,
    i.order_id,
    i.instalment_no,
    i.instalments,
    i.payment_type,
    i.customer_state,
    i.order_date,
    i.cash_date,
    i.amount,
    case when i.cash_date is null       then 'Never paid'
         when i.cash_date <= r.report_date then 'Received'
         else 'Due'
    end as status,
    coalesce(i.confirmed_late, false) as is_late
from instalment i
cross join (select max(order_approved_at)::date as report_date from silver.orders) r;

alter table gold.instalment add primary key (payment_id, instalment_no);
