-- Silver layer: the five Bronze tables typed and keyed, one row per Bronze row. No rule, nothing renamed.
-- load.py refused every value that would not convert (bronze.quarantine), and checks after this file
-- that each Silver table holds as many rows as its Bronze table.

drop schema if exists silver cascade;
create schema silver;

create table silver.orders as
select order_id,
       customer_id,
       order_purchase_timestamp::timestamp as order_purchase_timestamp,
       order_approved_at::timestamp        as order_approved_at          -- when the payment was confirmed; empty if never
from bronze.orders;

create table silver.order_payments as
select order_id,
       payment_sequential::int             as payment_sequential,        -- 1, 2 ... when one order is paid several ways
       payment_type,                                                     -- a code in silver.payment_methods
       payment_installments::int           as payment_installments,      -- how many instalments, not when they are paid
       payment_value::numeric(12, 2)       as payment_value
from bronze.order_payments;

create table silver.customers as
select customer_id,
       customer_state                                                    -- a code in silver.regions
from bronze.customers;

create table silver.payment_methods as
select payment_type,
       payment_method,                                                   -- the name the report shows
       sort_order::int                     as sort_order
from bronze.payment_methods;

create table silver.regions as
select customer_state, state, region
from bronze.regions;

alter table silver.orders          add primary key (order_id);
alter table silver.order_payments  add primary key (order_id, payment_sequential);
alter table silver.customers       add primary key (customer_id);
alter table silver.payment_methods add primary key (payment_type);
alter table silver.regions         add primary key (customer_state);
