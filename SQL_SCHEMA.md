# SQL Database Schema
## Hackathon Backend - MySQL Database

## Database Information
- **Database Name**: `hackathon_db`
- **Database Type**: MySQL 8.0
- **ORM**: SQLAlchemy (Python)
- **Connection**: Via Docker container `hackathon_mysql`

## Tables Overview

### 1. Users Table
Stores user account information.

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

**Columns:**
- `id`: Primary key, auto-increment
- `username`: Unique username (indexed)
- `email`: Unique email (indexed)
- `hashed_password`: Bcrypt hashed password
- `full_name`: Optional full name
- `is_active`: Account status flag
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### 2. Products Table
Stores product catalog information.

```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    stock_quantity INT DEFAULT 0,
    category VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_category (category)
);
```

**Columns:**
- `id`: Primary key, auto-increment
- `name`: Product name (indexed)
- `description`: Product description (TEXT)
- `price`: Product price (FLOAT)
- `stock_quantity`: Available stock
- `category`: Product category (indexed)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### 3. Orders Table
Stores order information.

```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'cancelled') DEFAULT 'pending',
    total_amount FLOAT NOT NULL,
    shipping_address VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

**Columns:**
- `id`: Primary key, auto-increment
- `user_id`: Foreign key to users table (indexed)
- `status`: Order status enum (indexed)
- `total_amount`: Total order amount
- `shipping_address`: Delivery address
- `created_at`: Timestamp of creation (indexed)
- `updated_at`: Timestamp of last update

**Status Values:**
- `pending`: Order placed, not yet processed
- `processing`: Order being processed
- `completed`: Order completed
- `cancelled`: Order cancelled

### 4. Order Items Table
Stores individual items within an order.

```sql
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
);
```

**Columns:**
- `id`: Primary key, auto-increment
- `order_id`: Foreign key to orders table (indexed)
- `product_id`: Foreign key to products table (indexed)
- `quantity`: Quantity of product ordered
- `price`: Price at time of order
- `created_at`: Timestamp of creation

## Relationships

```
users (1) ────< (many) orders
orders (1) ────< (many) order_items
products (1) ────< (many) order_items
```

## Indexes

### Performance Indexes
- `users.username` - Fast user lookup
- `users.email` - Fast email lookup
- `products.name` - Fast product search
- `products.category` - Fast category filtering
- `orders.user_id` - Fast user order retrieval
- `orders.status` - Fast status filtering
- `orders.created_at` - Fast date-based queries
- `order_items.order_id` - Fast order item retrieval
- `order_items.product_id` - Fast product order history

## Sample Queries

### Get user with orders
```sql
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.id = 1
GROUP BY u.id;
```

### Get order with items
```sql
SELECT o.*, oi.product_id, oi.quantity, oi.price, p.name as product_name
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.id = 1;
```

### Get products by category
```sql
SELECT * FROM products
WHERE category = 'Electronics'
ORDER BY created_at DESC;
```

### Get user orders with total
```sql
SELECT o.*, SUM(oi.quantity * oi.price) as calculated_total
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.user_id = 1
GROUP BY o.id;
```

## Database Access

### Via Docker
```bash
# Access MySQL container
docker-compose exec mysql mysql -u root -proot_password hackathon_db

# Or with user credentials
docker-compose exec mysql mysql -u hackathon_user -phackathon_pass hackathon_db
```

### Connection String
```
mysql+pymysql://hackathon_user:hackathon_pass@mysql:3306/hackathon_db
```

### Environment Variables
- `DB_HOST`: mysql (container name)
- `DB_PORT`: 3306
- `DB_USER`: hackathon_user
- `DB_PASSWORD`: hackathon_pass
- `DB_NAME`: hackathon_db

## Initialization

Tables are created automatically via SQLAlchemy when the application starts:
```python
Base.metadata.create_all(bind=engine)
```

Or manually via script:
```bash
docker-compose exec backend python scripts/init_db.py
```

## Notes

- **Not Django ORM**: We're using SQLAlchemy, not Django's ORM
- **Auto-migration**: Tables are created automatically on first run
- **Cascade Delete**: Deleting a user deletes their orders (CASCADE)
- **Indexes**: Optimized for common query patterns
- **Timestamps**: Automatic created_at and updated_at tracking


