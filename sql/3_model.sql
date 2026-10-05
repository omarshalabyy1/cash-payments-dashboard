-- Step 3, Model: a star schema around mart.fact_instalment (one row per instalment).
-- The dimension keys are the natural codes (date, payment type, state). They never change,
-- so surrogate keys would add a lookup and nothing else.

-- Every day from the first order to the last instalment, so each day, month and year adds up.
create table mart.dim_date as
select
    d::date                     as date,
    extract(year from d)::int   as year,
    to_char(d, 'YYYY-MM')       as year_month,
    to_char(d, 'Dy')            as weekday,
    extract(isodow from d)::int as weekday_no   -- 1 = Monday; sorts the weekday column
from generate_series(
    (select min(order_date) from mart.fact_instalment),
    (select max(cash_date)  from mart.fact_instalment),
    interval '1 day'
) as d;

-- The payment methods and the states with their regions come from the client's two mapping files.
create table mart.dim_payment_method as
select payment_type, payment_method, sort_order from raw.payment_methods;

create table mart.dim_state as
select customer_state, state, region from raw.regions;

-- Keys: a fact row that points at a missing day, method or state fails the load here,
-- and the error names the code that is missing from the mapping file.
alter table mart.dim_date           add primary key (date);
alter table mart.dim_payment_method add primary key (payment_type);
alter table mart.dim_state          add primary key (customer_state);
alter table mart.fact_instalment
    add primary key (payment_id, instalment_no),
    add foreign key (payment_type)   references mart.dim_payment_method,
    add foreign key (customer_state) references mart.dim_state,
    add foreign key (order_date)     references mart.dim_date,
    add foreign key (cash_date)      references mart.dim_date;
