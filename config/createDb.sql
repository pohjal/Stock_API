CREATE TABLE order_table (
    id SERIAL PRIMARY KEY,
    price DECIMAL,
    quantity DECIMAL,
    type VARCHAR,
    createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trades (
    trade_id SERIAL PRIMARY KEY,
    traded_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    traded_price DECIMAL(20, 2) NOT NULL,
    traded_quantity INTEGER NOT NULL,
);


CREATE TABLE last_price_table (
    price DECIMAL,
    name VARCHAR,
    createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- sample data

INSERT INTO your_table_name (price, quantity, type)
VALUES (10.99, 5.0, 'sample_type'); 