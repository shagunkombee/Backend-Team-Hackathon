# Hackathon Backend - Observability-Focused System

## 🎯 Project Overview

This is a production-ready backend application built for the **Kombee Frontend & Backend Team Hackathon 2.0**. The project demonstrates comprehensive observability implementation with FastAPI, MySQL, and a complete observability stack (Prometheus, Loki, Tempo, Grafana).

**Focus**: 75% Observability | 25% Application

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Database**: MySQL 8.0
- **Authentication**: JWT
- **Metrics**: Prometheus
- **Logs**: Loki + Promtail
- **Traces**: Tempo (via OpenTelemetry)
- **Visualization**: Grafana
- **Load Testing**: k6

## 📋 Features

### Application Features
- ✅ User Registration & Login (JWT)
- ✅ Product CRUD Operations
- ✅ Order Management
- ✅ Pagination & Filtering
- ✅ Input Validation
- ✅ Error Handling

### Observability Features
- ✅ **Metrics**: HTTP requests, latency, errors, DB queries
- ✅ **Logs**: Structured JSON logging with trace correlation
- ✅ **Traces**: End-to-end request tracing with custom spans
- ✅ **Dashboards**: 4 comprehensive Grafana dashboards
- ✅ **Anomaly Injection**: Built-in mechanisms for testing
- ✅ **Load Testing**: k6 scripts for realistic traffic

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git (optional)
- k6 (for load testing, optional)

### Installation

1. **Clone/Download the project**
```bash
cd backend_team_hackathon
```

2. **Start all services**
```bash
docker-compose up -d --build
```

3. **Initialize database**
```bash
docker-compose exec backend python scripts/init_db.py
```

4. **Verify services**
- Backend API: http://localhost:8000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

## 📚 Documentation

- **[High-Level Design (HLD)](docs/HIGH_LEVEL_DESIGN.md)** - System architecture and design
- **[Low-Level Design (LLD)](docs/LOW_LEVEL_DESIGN.md)** - Detailed implementation design
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Complete installation and configuration guide

## 🔍 Observability Stack

### Metrics (Prometheus)
- HTTP request count, duration, errors
- Database query duration and count
- Active users
- Custom business metrics

### Logs (Loki)
- Structured JSON logs
- Error tracking
- Login failures
- Validation errors
- Trace ID correlation

### Traces (Tempo)
- Full request lifecycle
- Custom spans for each layer
- Timing breakdown
- Bottleneck identification

### Dashboards (Grafana)
1. **Application Health Dashboard**
   - Requests per minute
   - Error rate %
   - 95th percentile latency
   - Slowest endpoints
   - Active users

2. **Database Performance Dashboard**
   - Query duration by operation
   - Slow queries
   - DB query rate
   - DB error rate

3. **Logs Dashboard**
   - Error logs
   - Login failures
   - Validation failures
   - Log count by severity
   - Trace ID filtering

4. **Traces Dashboard**
   - Trace search
   - Span duration breakdown
   - Trace count by service

## 🧪 Testing

### Load Testing with k6

```bash
cd load_test
k6 run k6_load_test.js
```

**Test Scenarios:**
- Ramp-up: 0 → 10 → 50 → 100 users
- Sustained load: 50 users
- Spike test: 100 users
- Total: 5,000+ requests

### Anomaly Injection

Enable anomalies in `docker-compose.yml`:

```yaml
environment:
  ENABLE_ANOMALY_DELAY: "True"
  ANOMALY_DELAY_SECONDS: "2.0"
  ENABLE_RANDOM_ERRORS: "True"
  RANDOM_ERROR_RATE: "0.1"
```

Then restart:
```bash
docker-compose restart backend
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (returns JWT)
- `GET /api/v1/auth/me` - Get current user (authenticated)

### Products
- `POST /api/v1/products` - Create product (authenticated)
- `GET /api/v1/products` - List products (pagination, filtering)
- `GET /api/v1/products/{id}` - Get product
- `PUT /api/v1/products/{id}` - Update product (authenticated)
- `DELETE /api/v1/products/{id}` - Delete product (authenticated)

### Orders
- `POST /api/v1/orders` - Create order (authenticated)
- `GET /api/v1/orders` - List orders (authenticated, paginated)
- `GET /api/v1/orders/{id}` - Get order (authenticated)

### System
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Backend | 8000 | FastAPI application |
| MySQL | 3306 | Database |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Visualization |
| Loki | 3100 | Log aggregation |
| Tempo | 3200, 4317, 4318 | Distributed tracing |

## 📁 Project Structure

```
backend_team_hackathon/
├── app/                    # FastAPI application
│   ├── core/              # Core functionality
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── api/               # API endpoints
├── prometheus/            # Prometheus config
├── loki/                  # Loki config
├── promtail/              # Promtail config
├── tempo/                 # Tempo config
├── grafana/               # Grafana dashboards & provisioning
├── load_test/             # k6 load testing scripts
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🔧 Configuration

### Environment Variables

Key configuration in `docker-compose.yml`:

- `DB_HOST`, `DB_USER`, `DB_PASSWORD` - Database connection
- `SECRET_KEY` - JWT secret key
- `OTEL_EXPORTER_OTLP_ENDPOINT` - Tempo endpoint
- `ENABLE_ANOMALY_DELAY` - Enable artificial delays
- `ENABLE_RANDOM_ERRORS` - Enable random errors

## 📝 Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart service
docker-compose restart [service_name]

# Execute command in container
docker-compose exec backend python scripts/init_db.py

# Rebuild after changes
docker-compose up -d --build
```

## 🎥 Video Submission Checklist

Before recording your submission video:

- [ ] All services running
- [ ] Database initialized
- [ ] Grafana dashboards imported
- [ ] Can demonstrate:
  - [ ] Working API endpoints
  - [ ] Metrics in Grafana
  - [ ] Logs in Loki
  - [ ] Full trace end-to-end
  - [ ] Anomaly injection impact
  - [ ] Load test execution
  - [ ] Before/after anomaly comparison

## 🏆 Scoring Breakdown (100 Marks)

- **Application**: 10 marks
- **Docker Setup**: 10 marks
- **Metrics**: 15 marks
- **Logs**: 15 marks
- **Traces**: 20 marks ⭐ (Highest)
- **Dashboards**: 15 marks
- **Anomaly Injection**: 10 marks
- **Load Testing**: 5 marks

## 🐛 Troubleshooting

See [Setup Guide](docs/SETUP_GUIDE.md) for detailed troubleshooting steps.

Common issues:
- Port conflicts: Check if ports are already in use
- Database connection: Wait for MySQL to be ready
- No metrics: Verify Prometheus targets
- No logs: Check Promtail configuration
- No traces: Verify OTLP endpoint

## 📄 License

This project is created for Kombee Technologies Hackathon 2.0.

## 👥 Author

Backend Team - Python Stack

---

**Deadline**: 14th March, 8:00 PM

**Submission**: GitHub repository link + Video recording


