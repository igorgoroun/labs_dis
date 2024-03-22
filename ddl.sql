create table product
(
    id serial primary key,
    sku varchar(32) not null unique,
    model        varchar,
    description  varchar,
    rrp          double precision default 0.0,
    create_date  timestamp        default CURRENT_TIMESTAMP,
    product_type varchar(8)       default 'product'::character varying not null
        constraint check_product_type
            check ((product_type)::text = ANY
                   ((ARRAY ['product'::character varying, 'service'::character varying])::text[]))
);
alter table product owner to igor;