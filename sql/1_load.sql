-- Step 1, Load: the three source files as they are, one raw table each.
-- load.py fills them with COPY; nothing is cleaned or renamed here.

drop schema if exists raw cascade;
create schema raw;

create table raw.orders (
    order_id                      text primary key,
    customer_id                   text not null,
    order_status                  text not null,
    order_purchase_timestamp      timestamp not null,
    order_approved_at             timestamp,          -- when the payment was confirmed; empty if never
    order_delivered_carrier_date  timestamp,
    order_delivered_customer_date timestamp,
    order_estimated_delivery_date timestamp
);

create table raw.order_payments (
    order_id             text not null,
    payment_sequential   int not null,                -- 1, 2 ... when one order is paid several ways
    payment_type         text not null,               -- credit_card, boleto, voucher, debit_card, not_defined
    payment_installments int not null,                -- how many instalments, not when they are paid
    payment_value        numeric(12, 2) not null,
    primary key (order_id, payment_sequential)
);

create table raw.customers (
    customer_id              text primary key,
    customer_unique_id       text not null,
    customer_zip_code_prefix text not null,
    customer_city            text not null,
    customer_state           char(2) not null
);
