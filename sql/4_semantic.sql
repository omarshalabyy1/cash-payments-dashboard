-- Semantic layer: the star schema Power BI imports. semantic.fact_instalment (one row per instalment) from
-- the Gold layer, and three dimensions built from the calendar setting and the Silver layer, never from the fact.
-- The dimension keys are the natural codes (date, payment type, state). They never change,
-- so surrogate keys would add a lookup and nothing else.

drop schema if exists semantic cascade;
create schema semantic;

create table semantic.fact_instalment as
select payment_id, order_id, instalment_no, instalments, payment_type, customer_state,
       order_date, cash_date, amount, status, is_late
from gold.instalment;

-- Every day of the fixed range calendar.start to calendar.end (config/client.yaml), passed in by load.py,
-- so each day, month and year adds up.
create table semantic.dim_date as
select
    d::date                     as date,
    extract(year from d)::int   as year,
    to_char(d, 'YYYY-MM')       as year_month,
    to_char(d, 'Dy')            as weekday,
    extract(isodow from d)::int as weekday_no   -- 1 = Monday; sorts the weekday column
from generate_series(
    current_setting('client.date_start')::date,
    current_setting('client.date_end')::date,
    interval '1 day'
) as d;

-- The payment methods and the states with their regions come from the client's two mapping files.
create table semantic.dim_payment_method as
select payment_type, payment_method, sort_order from silver.payment_methods;

create table semantic.dim_state as
select customer_state, state, region from silver.regions;

-- Keys: a fact row that points at a missing day, method or state fails the load here,
-- and the error names the code that is missing from the mapping file or the date outside the calendar.
alter table semantic.dim_date           add primary key (date);
alter table semantic.dim_payment_method add primary key (payment_type);
alter table semantic.dim_state          add primary key (customer_state);
alter table semantic.fact_instalment
    add primary key (payment_id, instalment_no),
    add foreign key (payment_type)   references semantic.dim_payment_method,
    add foreign key (customer_state) references semantic.dim_state,
    add foreign key (order_date)     references semantic.dim_date,
    add foreign key (cash_date)      references semantic.dim_date;
