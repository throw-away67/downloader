
INSERT INTO customers (name, email, credit, is_active) VALUES
('Alice Novak', 'alice@example.com', 100.0, TRUE),
('Bob Svoboda', 'bob@example.com', 50.0, TRUE),
('Carol Dvorak', 'carol@example.com', 0.0, TRUE);

INSERT INTO categories (name, is_active) VALUES
('Electronics', TRUE),
('Books', TRUE),
('Home', TRUE);

INSERT INTO products (name, price, stock, is_active) VALUES
('Smartphone Model X', 299.99, 15, TRUE),
('USB-C Charger', 19.99, 50, TRUE),
('Python Programming Book', 39.90, 30, TRUE),
('Coffee Maker', 79.00, 20, TRUE);

-- Assign products to categories (M:N)
INSERT INTO product_categories (product_id, category_id) VALUES
(1, 1), -- Smartphone -> Electronics
(2, 1), -- Charger -> Electronics
(3, 2), -- Book -> Books
(4, 3); -- Coffee Maker -> Home