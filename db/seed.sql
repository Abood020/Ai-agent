
INSERT INTO books (isbn, title, author, price, stock) VALUES
('9780132350884', 'Clean Code', 'Robert C. Martin', 45.00, 12),
('9780201616224', 'The Pragmatic Programmer', 'Andrew Hunt', 50.00, 8),
('9780131103627', 'The C Programming Language', 'Brian W. Kernighan', 40.00, 5),
('9781491950357', 'Designing Data-Intensive Applications', 'Martin Kleppmann', 65.00, 7),
('9780134494166', 'Clean Architecture', 'Robert C. Martin', 48.00, 6),
('9781492043454', 'Fluent Python', 'Luciano Ramalho', 55.00, 10),
('9781617296086', 'Spring in Action', 'Craig Walls', 52.00, 4),
('9780135957059', 'Refactoring', 'Martin Fowler', 60.00, 9),
('9781492078005', 'Kubernetes: Up and Running', 'Kelsey Hightower', 58.00, 3),
('9781491904244', 'You Don’t Know JS', 'Kyle Simpson', 35.00, 15);

INSERT INTO customers (name, email) VALUES
('Alice Johnson', 'alice@example.com'),
('Bob Smith', 'bob@example.com'),
('Charlie Brown', 'charlie@example.com'),
('Diana Prince', 'diana@example.com'),
('Ethan Clark', 'ethan@example.com'),
('Fatima Ali', 'fatima@example.com');

(1, 'completed'),
(2, 'pending'),
(3, 'shipped'),
(2, 'completed');

INSERT INTO order_items (order_id, isbn, qty, price_at_order) VALUES
(1, '9780132350884', 1, 45.00), 
(1, '9780201616224', 1, 50.00),  
(2, '9780201616224', 2, 50.00),
(3, '9780131103627', 1, 40.00),
(4, '9781491950357', 1, 65.00);
