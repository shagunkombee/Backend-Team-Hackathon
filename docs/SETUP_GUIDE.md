# Setup and Installation Guide
## Complete Step-by-Step Instructions

### Prerequisites

1. **Docker & Docker Compose**
   - Docker Desktop (Windows/Mac) or Docker Engine (Linux)
   - Docker Compose v2.0+

2. **Git** (for cloning repository)

3. **k6** (optional, for load testing)
   - Download from: https://k6.io/docs/getting-started/installation/

### Step 1: Clone/Download Project

```bash
# If using Git
git clone <repository-url>
cd backend_team_hackathon

# Or extract the project folder if downloaded as ZIP
```

### Step 2: Verify Project Structure

Ensure you have the following structure:
```
backend_team_hackathon/
├── app/
├── prometheus/
├── loki/
├── promtail/
├── tempo/
├── grafana/
├── load_test/
├── scripts/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Step 3: Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
```

### Step 4: Initialize Database

```bash
# Wait for MySQL to be ready (about 30 seconds)
# Then initialize database with tables and seed data
docker-compose exec backend python scripts/init_db.py
```

**Expected Output:**
```
✓ Admin user created (username: admin, password: admin123)
✓ Created 5 test products
✓ Database initialization completed
```

### Step 5: Verify Services

#### 5.1 Backend API
```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"hackathon-backend","version":"1.0.0"}

# Metrics endpoint
curl http://localhost:8000/metrics
```

#### 5.2 Prometheus
- Open browser: http://localhost:9090
- Check targets: Status → Targets
- Verify `backend` target is UP

#### 5.3 Grafana
- Open browser: http://localhost:3000
- Login: `admin` / `admin`
- Verify datasources:
  - Prometheus (http://prometheus:9090)
  - Loki (http://loki:3100)
  - Tempo (http://tempo:3200)

#### 5.4 Tempo
```bash
# Check Tempo health
curl http://localhost:3200/ready
```

#### 5.5 Loki
```bash
# Check Loki health
curl http://localhost:3100/ready
```

### Step 6: Test API Endpoints

#### 6.1 Register a User
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

#### 6.2 Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

**Save the `access_token` from response for next steps.**

#### 6.3 Create Product (Authenticated)
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Test Product",
    "description": "A test product",
    "price": 99.99,
    "stock_quantity": 100,
    "category": "Electronics"
  }'
```

#### 6.4 List Products
```bash
curl http://localhost:8000/api/v1/products?limit=10
```

#### 6.5 Create Order (Authenticated)
```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "price": 99.99
      }
    ],
    "shipping_address": "123 Test Street"
  }'
```

### Step 7: Setup Grafana Dashboards

#### 7.1 Import Dashboards

1. Go to Grafana: http://localhost:3000
2. Navigate to: Dashboards → Import
3. Import each dashboard JSON file:
   - `grafana/dashboards/application-health.json`
   - `grafana/dashboards/database-performance.json`
   - `grafana/dashboards/logs-dashboard.json`
   - `grafana/dashboards/traces-dashboard.json`

**OR** (if auto-provisioning works):
- Dashboards should auto-load from `grafana/dashboards/` folder
- Check: Dashboards → Browse

#### 7.2 Verify Dashboard Data

1. **Application Health Dashboard**
   - Generate some traffic (make API calls)
   - Check if metrics appear in graphs

2. **Database Performance Dashboard**
   - Should show DB query metrics after API calls

3. **Logs Dashboard**
   - Should show structured logs from backend

4. **Traces Dashboard**
   - Make a request and check trace ID in response headers
   - Search for trace in Tempo

### Step 8: Inject Anomalies (Testing)

#### 8.1 Enable Artificial Delay

Edit `docker-compose.yml`, update backend environment:
```yaml
environment:
  ENABLE_ANOMALY_DELAY: "True"
  ANOMALY_DELAY_SECONDS: "2.0"
```

Restart backend:
```bash
docker-compose restart backend
```

**Test:**
- Make API calls
- Check latency increase in Grafana
- View trace spans showing delay

#### 8.2 Enable Random Errors

Edit `docker-compose.yml`, update backend environment:
```yaml
environment:
  ENABLE_RANDOM_ERRORS: "True"
  RANDOM_ERROR_RATE: "0.1"  # 10% error rate
```

Restart backend:
```bash
docker-compose restart backend
```

**Test:**
- Make multiple API calls
- Check error rate increase in Grafana
- View error logs in Loki

### Step 9: Run Load Tests

#### 9.1 Install k6 (if not installed)

**Windows:**
```powershell
# Using Chocolatey
choco install k6

# Or download from: https://k6.io/docs/getting-started/installation/
```

**Linux/Mac:**
```bash
# Using package manager
sudo apt-get install k6  # Ubuntu/Debian
brew install k6          # Mac
```

#### 9.2 Run Load Test

```bash
# Navigate to load_test directory
cd load_test

# Run load test
k6 run k6_load_test.js

# Or with custom base URL
k6 run --env BASE_URL=http://localhost:8000 k6_load_test.js
```

**Expected Output:**
- Test stages execution
- Metrics summary
- Pass/fail status

#### 9.3 Monitor During Load Test

1. **Grafana Dashboards**: Watch metrics in real-time
2. **Prometheus**: Check raw metrics
3. **Loki**: Monitor log volume
4. **Tempo**: View trace distribution

### Step 10: View Trace End-to-End

#### 10.1 Make a Request and Get Trace ID

```bash
# Make a request
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"items": [{"product_id": 1, "quantity": 1, "price": 99.99}]}' \
  -v

# Check response headers for X-Trace-ID
```

#### 10.2 Search Trace in Grafana

1. Go to Grafana → Explore → Tempo
2. Enter trace ID in search
3. View full trace breakdown:
   - HTTP request span
   - Database query spans
   - Service layer spans
   - Timing for each span

### Step 11: Common Commands Reference

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart [service_name]

# Execute command in container
docker-compose exec backend python scripts/init_db.py

# Rebuild after code changes
docker-compose up -d --build

# Check service health
docker-compose ps

# View resource usage
docker stats
```

### Step 12: Troubleshooting

#### Issue: Services won't start
```bash
# Check logs
docker-compose logs

# Check if ports are already in use
netstat -an | grep :8000  # Windows
lsof -i :8000              # Mac/Linux
```

#### Issue: Database connection errors
```bash
# Wait for MySQL to be ready
docker-compose logs mysql

# Check MySQL health
docker-compose exec mysql mysqladmin ping -h localhost -u root -proot_password
```

#### Issue: No metrics in Prometheus
```bash
# Check if backend is being scraped
# Visit: http://localhost:9090/targets
# Verify backend target is UP

# Check backend metrics endpoint
curl http://localhost:8000/metrics
```

#### Issue: No logs in Loki
```bash
# Check Promtail logs
docker-compose logs promtail

# Verify log files exist
docker-compose exec backend ls -la /var/log/app/
```

#### Issue: No traces in Tempo
```bash
# Check backend logs for OTLP errors
docker-compose logs backend | grep -i otlp

# Verify Tempo is accessible
curl http://localhost:3200/ready
```

### Step 13: Production Considerations

1. **Change Default Passwords**: Update all default credentials
2. **Secure JWT Secret**: Use strong, random secret key
3. **Enable HTTPS**: Use reverse proxy (nginx/traefik)
4. **Resource Limits**: Add resource limits in docker-compose.yml
5. **Backup Strategy**: Regular database backups
6. **Monitoring Alerts**: Configure Grafana alerts
7. **Log Retention**: Configure log retention policies

### Step 14: Video Recording Checklist

Before recording your submission video, ensure:

- [ ] All services are running
- [ ] Database is initialized with test data
- [ ] Grafana dashboards are imported and showing data
- [ ] You can demonstrate:
  - [ ] Working application (API calls)
  - [ ] Metrics in Grafana
  - [ ] Logs in Loki
  - [ ] Full trace end-to-end
  - [ ] Anomaly injection and its impact
  - [ ] Load test execution
  - [ ] Before/after anomaly comparison


