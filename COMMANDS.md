# Quick Commands Reference

## Docker Commands

### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start and build (after code changes)
docker-compose up -d --build

# Start with logs visible
docker-compose up
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f mysql
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Service Status
```bash
# Check running services
docker-compose ps

# Check resource usage
docker stats
```

### Execute Commands in Containers
```bash
# Run Python script
docker-compose exec backend python scripts/init_db.py

# Access MySQL
docker-compose exec mysql mysql -u root -proot_password hackathon_db

# Access backend shell
docker-compose exec backend bash
```

## API Testing Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

**Save the `access_token` from response!**

### Get Current User (Authenticated)
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Product
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock_quantity": 50,
    "category": "Electronics"
  }'
```

### List Products
```bash
# Basic list
curl http://localhost:8000/api/v1/products

# With pagination
curl "http://localhost:8000/api/v1/products?skip=0&limit=10"

# With filtering
curl "http://localhost:8000/api/v1/products?category=Electronics&min_price=100&max_price=1000"

# With search
curl "http://localhost:8000/api/v1/products?search=laptop"
```

### Get Product
```bash
curl http://localhost:8000/api/v1/products/1
```

### Update Product
```bash
curl -X PUT http://localhost:8000/api/v1/products/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "price": 899.99,
    "stock_quantity": 45
  }'
```

### Delete Product
```bash
curl -X DELETE http://localhost:8000/api/v1/products/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Order
```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "price": 999.99
      }
    ],
    "shipping_address": "123 Test Street, Test City"
  }'
```

### List Orders
```bash
curl http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# With pagination
curl "http://localhost:8000/api/v1/orders?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Order
```bash
curl http://localhost:8000/api/v1/orders/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Metrics (Prometheus)
```bash
curl http://localhost:8000/metrics
```

## Load Testing Commands

### Run k6 Load Test
```bash
cd load_test
k6 run k6_load_test.js
```

### Run with Custom URL
```bash
k6 run --env BASE_URL=http://localhost:8000 k6_load_test.js
```

### Run with Different VUs (Virtual Users)
```bash
# Edit k6_load_test.js stages or use:
k6 run --vus 50 --duration 5m k6_load_test.js
```

## Anomaly Injection

### Enable Delay Anomaly
1. Edit `docker-compose.yml`:
```yaml
backend:
  environment:
    ENABLE_ANOMALY_DELAY: "True"
    ANOMALY_DELAY_SECONDS: "2.0"
```

2. Restart:
```bash
docker-compose restart backend
```

### Enable Random Errors
1. Edit `docker-compose.yml`:
```yaml
backend:
  environment:
    ENABLE_RANDOM_ERRORS: "True"
    RANDOM_ERROR_RATE: "0.1"
```

2. Restart:
```bash
docker-compose restart backend
```

## Database Commands

### Access MySQL
```bash
docker-compose exec mysql mysql -u root -proot_password hackathon_db
```

### MySQL Commands (inside MySQL)
```sql
-- Show tables
SHOW TABLES;

-- Describe table
DESCRIBE users;
DESCRIBE products;
DESCRIBE orders;
DESCRIBE order_items;

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;

-- View users
SELECT id, username, email, created_at FROM users;

-- View products
SELECT id, name, price, stock_quantity FROM products;

-- View orders
SELECT id, user_id, status, total_amount, created_at FROM orders;
```

### Backup Database
```bash
docker-compose exec mysql mysqldump -u root -proot_password hackathon_db > backup.sql
```

### Restore Database
```bash
docker-compose exec -T mysql mysql -u root -proot_password hackathon_db < backup.sql
```

## Observability Commands

### Check Prometheus Targets
```bash
# Visit in browser: http://localhost:9090/targets
# Or check via API:
curl http://localhost:9090/api/v1/targets
```

### Check Loki Health
```bash
curl http://localhost:3100/ready
```

### Check Tempo Health
```bash
curl http://localhost:3200/ready
```

### Query Prometheus
```bash
# Example: Get request rate
curl 'http://localhost:9090/api/v1/query?query=rate(http_requests_total[1m])'
```

### Search Logs in Loki (via API)
```bash
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={job="backend"}' \
  --data-urlencode 'start=1640995200000000000' \
  --data-urlencode 'end=1640998800000000000' \
  --data-urlencode 'limit=100'
```

## Troubleshooting Commands

### Check Port Usage
```bash
# Windows
netstat -an | findstr :8000
netstat -an | findstr :3306
netstat -an | findstr :3000

# Linux/Mac
lsof -i :8000
lsof -i :3306
lsof -i :3000
```

### Check Container Logs
```bash
# All containers
docker-compose logs

# Last 100 lines
docker-compose logs --tail=100

# Follow logs
docker-compose logs -f
```

### Check Container Status
```bash
# Detailed status
docker-compose ps

# Resource usage
docker stats

# Container details
docker inspect hackathon_backend
```

### Restart Everything
```bash
# Stop all
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v

# Start fresh
docker-compose up -d --build
```

### Clean Up
```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune
```

## Development Commands

### Install Dependencies Locally
```bash
pip install -r requirements.txt
```

### Run Locally (without Docker)
```bash
# Set environment variables
export DB_HOST=localhost
export DB_USER=hackathon_user
export DB_PASSWORD=hackathon_pass
export DB_NAME=hackathon_db

# Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Database Initialization
```bash
# In Docker
docker-compose exec backend python scripts/init_db.py

# Locally
python scripts/init_db.py
```

### Run Tests (if available)
```bash
# In Docker
docker-compose exec backend pytest

# Locally
pytest
```

## Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Loki | http://localhost:3100 | - |
| Tempo | http://localhost:3200 | - |


