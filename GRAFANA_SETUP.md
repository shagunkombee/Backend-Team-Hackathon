# Grafana Setup Guide - Simple Steps

## Step 1: Access Grafana

1. Open your browser
2. Go to: **http://localhost:3000**
3. Login with:
   - Username: `admin`
   - Password: `admin`

---

## Step 2: Configure Data Sources (One Time Setup)

### A. Add Prometheus Data Source

1. Click **⚙️ Configuration** (left sidebar) → **Data sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Set URL: `http://prometheus:9090`
5. Click **Save & test** (should show "Data source is working")

### B. Add Loki Data Source

1. Click **Add data source** again
2. Select **Loki**
3. Set URL: `http://loki:3100`
4. Click **Save & test**

### C. Add Tempo Data Source

1. Click **Add data source** again
2. Select **Tempo**
3. Set URL: `http://tempo:3200`
4. Click **Save & test**

---

## Step 3: Create Dashboards (Easy Way)

### Dashboard 1: Application Health

1. Click **+** (left sidebar) → **Create** → **Dashboard**
2. Click **Add visualization**
3. Select **Prometheus** data source
4. Add these panels one by one:

#### Panel 1: Requests Per Minute
- **Query**: `rate(http_requests_total[1m]) * 60`
- **Title**: Requests Per Minute
- Click **Apply**

#### Panel 2: Error Rate
- **Query**: `rate(http_errors_total[1m]) / rate(http_requests_total[1m]) * 100`
- **Title**: Error Rate %
- Click **Apply**

#### Panel 3: 95th Percentile Latency
- **Query**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Title**: 95th Percentile Latency
- Click **Apply**

#### Panel 4: Slowest Endpoints
- **Query**: `topk(10, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))`
- **Title**: Slowest Endpoints
- **Visualization**: Table
- Click **Apply**

5. Click **Save dashboard** (top right)
6. Name it: **Application Health**

---

### Dashboard 2: Database Performance

1. Create new dashboard
2. Add panels:

#### Panel 1: Query Duration
- **Query**: `rate(db_query_duration_seconds_sum[1m]) / rate(db_query_duration_seconds_count[1m])`
- **Title**: Average Query Duration

#### Panel 2: Slow Queries
- **Query**: `topk(10, histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m])))`
- **Title**: Slow Queries
- **Visualization**: Table

3. Save as: **Database Performance**

---

### Dashboard 3: Logs

1. Create new dashboard
2. Click **Add visualization**
3. Select **Loki** data source
4. **Query**: `{job="backend"}`
5. **Visualization**: Logs
6. Save as: **Application Logs**

---

## Step 4: Quick Test Queries

### In Grafana Explore (for testing):

1. Click **Explore** (compass icon, left sidebar)
2. Select **Prometheus** data source
3. Try these queries:

```
# Total requests
http_requests_total

# Request rate
rate(http_requests_total[1m])

# Error rate
rate(http_errors_total[1m])

# Latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

---

## Troubleshooting

### If no data shows:
1. Make some API requests first:
   ```powershell
   curl http://localhost:8001/api/v1/products
   curl http://localhost:8001/health
   ```

2. Check Prometheus targets:
   - Go to Prometheus: http://localhost:9090
   - Click **Status** → **Targets**
   - Verify `backend` is UP

### If datasource connection fails:
- Check service names match docker-compose.yml
- URLs should be: `http://prometheus:9090` (not localhost!)

---

## Quick Reference

**Grafana URL**: http://localhost:3000
**Login**: admin / admin

**Prometheus URL**: http://localhost:9090
**Backend API**: http://localhost:8001

