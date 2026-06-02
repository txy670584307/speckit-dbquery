-- ==========================================================
-- DB Query Tool 测试数据
-- 执行方式：docker exec -i pg-test psql -U postgres -d testdb < data/sample_data.sql
-- ==========================================================

-- 创建测试 schema
CREATE SCHEMA IF NOT EXISTS sales;

-- 用户表
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO public.users (username, email, full_name, is_active) VALUES
    ('alice', 'alice@example.com', 'Alice Wang', true),
    ('bob', 'bob@example.com', 'Bob Li', true),
    ('charlie', 'charlie@example.com', 'Charlie Zhang', false),
    ('diana', 'diana@example.com', 'Diana Chen', true),
    ('eve', 'eve@example.com', 'Eve Liu', true);

-- 产品表
CREATE TABLE IF NOT EXISTS public.products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO public.products (name, category, price, stock) VALUES
    ('机械键盘', '电子产品', 299.00, 50),
    ('无线鼠标', '电子产品', 89.00, 120),
    ('27寸显示器', '电子产品', 1599.00, 30),
    ('办公桌', '家具', 699.00, 15),
    ('人体工学椅', '家具', 1299.00, 25),
    ('笔记本支架', '配件', 59.00, 200);

-- 订单表
CREATE TABLE IF NOT EXISTS sales.orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES public.users(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);

INSERT INTO sales.orders (user_id, total_amount, status) VALUES
    (1, 598.00, 'completed'),
    (1, 89.00, 'completed'),
    (2, 1599.00, 'completed'),
    (3, 699.00, 'cancelled'),
    (4, 2589.00, 'completed'),
    (5, 59.00, 'pending'),
    (1, 1299.00, 'pending'),
    (4, 299.00, 'completed');

-- 订单明细表
CREATE TABLE IF NOT EXISTS sales.order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES sales.orders(id),
    product_id INT NOT NULL REFERENCES public.products(id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

INSERT INTO sales.order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 2, 299.00),
    (2, 2, 1, 89.00),
    (3, 3, 1, 1599.00),
    (4, 4, 1, 699.00),
    (5, 5, 1, 1299.00),
    (5, 6, 10, 59.00),
    (6, 6, 1, 59.00),
    (7, 5, 1, 1299.00),
    (8, 1, 1, 299.00);
