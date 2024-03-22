drop table if exists product;
create table product
(
    id   int          not null AUTO_INCREMENT,
    sku varchar(32) not null unique,
    model        varchar(128),
    description  varchar(255),
    rrp          double precision default 0.0,
    create_date  timestamp        default CURRENT_TIMESTAMP,
    product_type varchar(8)       not null default 'product',
    primary key (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci AUTO_INCREMENT=1;
