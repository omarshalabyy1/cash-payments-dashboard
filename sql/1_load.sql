-- Step 1, Load: the five input files as they are, one raw table each, only the columns the rules use.
-- load.py checks each file and fills these tables with COPY; nothing is cleaned or renamed here.

drop schema if exists raw cascade;
create schema raw;

create table raw.orders (
    order_id                 text primary key,
    customer_id              text not null,
    order_purchase_timestamp timestamp not null,
    order_approved_at        timestamp            -- when the payment was confirmed; empty if never
);

create table raw.order_payments (
    order_id             text not null,
    payment_sequential   int not null,            -- 1, 2 ... when one order is paid several ways
    payment_type         text not null,           -- a code in raw.payment_methods
    payment_installments int not null,            -- how many instalments, not when they are paid
    payment_value        numeric(12, 2) not null,
    primary key (order_id, payment_sequential)
);

create table raw.customers (
    customer_id    text primary key,
    customer_state text not null                  -- a code in raw.regions
);

create table raw.payment_methods (
    payment_type   text primary key,
    payment_method text not null,                 -- the name the report shows
    sort_order     int not null
);

create table raw.regions (
    customer_state text primary key,
    state          text not null,
    region         text not null
);
