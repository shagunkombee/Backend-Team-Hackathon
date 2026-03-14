# Low-Level Design (LLD)
## Hackathon Backend - Detailed Implementation Design

### 1. Application Structure

```
backend_team_hackathon/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Application configuration
│   │   ├── database.py             # Database setup and session management
│   │   ├── observability.py       # OpenTelemetry setup
│   │   └── security.py             # JWT and password hashing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User model
│   │   ├── product.py             # Product model
│   │   └── order.py               # Order and OrderItem models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                # User Pydantic schemas
│   │   ├── product.py             # Product Pydantic schemas
│   │   └── order.py               # Order Pydantic schemas
│   └── api/
│       └── v1/
│           ├── __init__.py        # API router aggregation
│           ├── auth.py            # Authentication endpoints
│           ├── products.py        # Product CRUD endpoints
│           └── orders.py          # Order CRUD endpoints
├── prometheus/
│   └── prometheus.yml             # Prometheus configuration
├── loki/
│   └── loki-config.yml            # Loki configuration
├── promtail/
│   └── promtail-config.yml        # Promtail configuration
├── tempo/
│   └── tempo-config.yml           # Tempo configuration
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── datasources.yml
│   │   └── dashboards/
│   │       └── dashboards.yml
│   └── dashboards/
│       ├── application-health.json
│       ├── database-performance.json
│       ├── logs-dashboard.json
│       └── traces-dashboard.json
├── load_test/
│   └── k6_load_test.js            # k6 load testing script
├── scripts/
│   ├── init_db.py                 # Database initialization
│   └── inject_anomaly.py          # Anomaly injection helper
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### 2. Database Schema

#### 2.1 Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
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

#### 2.2 Products Table
```sql
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
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

#### 2.3 Orders Table
```sql
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'cancelled') DEFAULT 'pending',
    total_amount FLOAT NOT NULL,
    shipping_address VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 2.4 Order Items Table
```sql
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
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

### 3. API Endpoints

#### 3.1 Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (returns JWT)
- `GET /api/v1/auth/me` - Get current user info

#### 3.2 Product Endpoints
- `POST /api/v1/products` - Create product (authenticated)
- `GET /api/v1/products` - List products (with pagination, filtering)
- `GET /api/v1/products/{id}` - Get single product
- `PUT /api/v1/products/{id}` - Update product (authenticated)
- `DELETE /api/v1/products/{id}` - Delete product (authenticated)

#### 3.3 Order Endpoints
- `POST /api/v1/orders` - Create order (authenticated)
- `GET /api/v1/orders` - List user's orders (authenticated, paginated)
- `GET /api/v1/orders/{id}` - Get single order (authenticated)

#### 3.4 System Endpoints
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics endpoint

### 4. Observability Implementation Details

#### 4.1 Metrics (Prometheus)

**HTTP Metrics:**
```python
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)
```

**Database Metrics:**
```python
DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table']
)
```

#### 4.2 Logging (Loki)

**Structured Logging Format:**
```json
{
  "timestamp": "2024-03-14T10:30:00Z",
  "level": "INFO",
  "service": "backend",
  "message": "HTTP request",
  "method": "POST",
  "path": "/api/v1/orders",
  "status_code": 201,
  "duration_ms": 45.2,
  "trace_id": "abc123..."
}
```

#### 4.3 Tracing (OpenTelemetry → Tempo)

**Trace Span Hierarchy:**
```
HTTP Request (Root Span)
├── auth.login (if login endpoint)
│   ├── db.select (user lookup)
│   └── jwt.create_token
├── products.create
│   ├── validation
│   └── db.insert
└── orders.create
    ├── orders.validate_items
    │   └── db.select (product lookup)
    └── orders.create_db_transaction
        ├── db.insert (order)
        ├── db.insert (order_items)
        └── db.update (product stock)
```

### 5. Anomaly Injection Mechanisms

#### 5.1 Artificial Delay
```python
if settings.ENABLE_ANOMALY_DELAY:
    time.sleep(settings.ANOMALY_DELAY_SECONDS)
```

**Impact:**
- Increases latency metrics
- Shows up in trace spans as long duration
- Affects 95th percentile calculations

#### 5.2 Random Errors
```python
if settings.ENABLE_RANDOM_ERRORS and random.random() < settings.RANDOM_ERROR_RATE:
    raise HTTPException(status_code=500, detail="Random error")
```

**Impact:**
- Increases error rate metrics
- Creates error logs
- Generates error traces

#### 5.3 Inefficient Queries
- Simulated by adding delays to query-heavy endpoints
- Can be enhanced by removing indexes (manual DB operation)

### 6. Load Testing Strategy

#### 6.1 k6 Test Scenarios
1. **Ramp-up Phase**: Gradually increase users (1m → 10 users)
2. **Sustained Load**: Maintain 50 users (2m)
3. **Spike Test**: Sudden increase to 100 users (3m)
4. **Ramp-down**: Gradually decrease to 0 (2m)

#### 6.2 Test Coverage
- User registration and login
- Product listing and retrieval
- Order creation
- Concurrent operations

### 7. Configuration Management

#### 7.1 Environment Variables
- Database connection settings
- JWT secret key and expiration
- Observability endpoints
- Anomaly injection flags

#### 7.2 Docker Compose Configuration
- Service networking
- Volume mounts
- Health checks
- Dependency management

### 8. Error Handling

#### 8.1 Error Types
- **Validation Errors**: 400 Bad Request
- **Authentication Errors**: 401 Unauthorized
- **Authorization Errors**: 403 Forbidden
- **Not Found Errors**: 404 Not Found
- **Server Errors**: 500 Internal Server Error

#### 8.2 Error Logging
- All errors logged with structured format
- Include trace ID for correlation
- Error type and message captured
- Stack traces for debugging

### 9. Performance Optimizations

1. **Database Connection Pooling**: Reuse connections efficiently
2. **Query Optimization**: Proper indexing on frequently queried columns
3. **Async Operations**: FastAPI async support for I/O operations
4. **Caching**: Can be added for frequently accessed data
5. **Pagination**: Limit data transfer for list endpoints

### 10. Security Implementation

1. **Password Hashing**: bcrypt with salt
2. **JWT Tokens**: HS256 algorithm with expiration
3. **Input Validation**: Pydantic schemas validate all inputs
4. **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
5. **CORS Configuration**: Configurable CORS settings


