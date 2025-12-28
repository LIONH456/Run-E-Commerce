USE minishop;

CREATE TABLE IF NOT EXISTS products (
  product_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(500),
  price DECIMAL(10,2) NOT NULL,
  stock INT NOT NULL,
  image_url VARCHAR(255),
  status VARCHAR(10) DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, description, price, stock, image_url, status) VALUES
('Coffee Mug', 'A nice mug.', 8.50, 100, '', 'ACTIVE'),
('T-Shirt', 'Cotton shirt', 15.00, 50, '', 'ACTIVE');
