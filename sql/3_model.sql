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

create table mart.dim_payment_method (
    payment_type   text primary key,
    payment_method text not null,
    sort_order     int not null
);
insert into mart.dim_payment_method values
    ('credit_card', 'Credit card',        1),
    ('boleto',      'Boleto (bank slip)', 2),
    ('voucher',     'Voucher',            3),
    ('debit_card',  'Debit card',         4),
    ('not_defined', 'Not defined',        5);

-- One row per customer state, with the region it belongs to.
create table mart.dim_state (
    customer_state char(2) primary key,
    state          text not null,
    region         text not null
);
insert into mart.dim_state values
    ('AC', 'Acre',                'North'),
    ('AP', 'Amapá',               'North'),
    ('AM', 'Amazonas',            'North'),
    ('PA', 'Pará',                'North'),
    ('RO', 'Rondônia',            'North'),
    ('RR', 'Roraima',             'North'),
    ('TO', 'Tocantins',           'North'),
    ('AL', 'Alagoas',             'Northeast'),
    ('BA', 'Bahia',               'Northeast'),
    ('CE', 'Ceará',               'Northeast'),
    ('MA', 'Maranhão',            'Northeast'),
    ('PB', 'Paraíba',             'Northeast'),
    ('PE', 'Pernambuco',          'Northeast'),
    ('PI', 'Piauí',               'Northeast'),
    ('RN', 'Rio Grande do Norte', 'Northeast'),
    ('SE', 'Sergipe',             'Northeast'),
    ('DF', 'Distrito Federal',    'Central-West'),
    ('GO', 'Goiás',               'Central-West'),
    ('MT', 'Mato Grosso',         'Central-West'),
    ('MS', 'Mato Grosso do Sul',  'Central-West'),
    ('ES', 'Espírito Santo',      'Southeast'),
    ('MG', 'Minas Gerais',        'Southeast'),
    ('RJ', 'Rio de Janeiro',      'Southeast'),
    ('SP', 'São Paulo',           'Southeast'),
    ('PR', 'Paraná',              'South'),
    ('RS', 'Rio Grande do Sul',   'South'),
    ('SC', 'Santa Catarina',      'South');

-- Keys: a fact row that points at a missing day, method or state fails the load here.
alter table mart.dim_date add primary key (date);
alter table mart.fact_instalment
    add primary key (payment_id, instalment_no),
    add foreign key (payment_type)   references mart.dim_payment_method,
    add foreign key (customer_state) references mart.dim_state,
    add foreign key (order_date)     references mart.dim_date,
    add foreign key (cash_date)      references mart.dim_date;
