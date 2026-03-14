# High-Level Design (HLD)
## Hackathon Backend - Observability-Focused System

### 1. System Overview

This system is a production-ready backend application built with FastAPI, MySQL, and a complete observability stack. The primary focus is on demonstrating production engineering maturity through comprehensive observability.

### 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│                    (Frontend / API Clients)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend Application                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Auth API   │  │  Products    │  │   Orders     │         │
│  │   (JWT)      │  │    API       │  │    API       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         Observability Middleware Layer                    │ │
│  │  • OpenTelemetry Instrumentation                         │ │
│  │  • Structured Logging (structlog)                        │ │
│  │  • Prometheus Metrics Collection                         │ │
│  │  • Request Tracing                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────┬──────────────────┬──────────────────┬─────────────┘
             │                  │                  │
    ┌────────▼────────┐  ┌──────▼──────┐  ┌───────▼────────┐
    │   MySQL DB      │  │  Prometheus │  │  Tempo (OTLP)   │
    │   (Data)        │  │  (Metrics)  │  │  (Traces)       │
    └─────────────────┘  └─────────────┘  └──────────────────┘
                                  │                  │
                                  │                  │
                         ┌────────▼──────────────────▼────────┐
                         │         Grafana                    │
                         │  • Metrics Visualization           │
                         │  • Log Aggregation (Loki)           │
                         │  • Trace Exploration (Tempo)        │
                         │  • Dashboards                       │
                         └─────────────────────────────────────┘
                                  │
                         ┌────────▼────────┐
                         │      Loki       │
                         │  (Log Storage)  │
                         └─────────────────┘
```

### 3. Component Breakdown

#### 3.1 Application Layer
- **FastAPI Framework**: Modern, fast Python web framework
- **JWT Authentication**: Secure token-based authentication
- **RESTful APIs**: Clean API design with proper HTTP methods
- **Database ORM**: SQLAlchemy for database abstraction

#### 3.2 Observability Stack

**Metrics (Prometheus)**
- HTTP request metrics (count, duration, errors)
- Database query metrics (duration, count, errors)
- Business metrics (active users, order counts)

**Logs (Loki)**
- Structured JSON logging
- Log aggregation and search
- Trace ID correlation

**Traces (Tempo via OpenTelemetry)**
- End-to-end request tracing
- Custom spans for each logical layer
- Timing breakdown per operation

**Visualization (Grafana)**
- Application Health Dashboard
- Database Performance Dashboard
- Logs Dashboard
- Traces Dashboard

#### 3.3 Data Layer
- **MySQL 8.0**: Relational database
- **Connection Pooling**: Optimized database connections
- **Query Instrumentation**: Automatic query timing and tracing

### 4. Data Flow

#### 4.1 Request Flow
1. Client sends HTTP request to FastAPI backend
2. Middleware captures request metadata
3. OpenTelemetry creates trace span
4. Request processed by appropriate endpoint
5. Database queries executed (with instrumentation)
6. Response returned with trace ID in headers
7. Metrics, logs, and traces sent to respective collectors

#### 4.2 Observability Data Flow
- **Metrics**: Backend → Prometheus (scraping every 5s)
- **Logs**: Backend → Loki (via Promtail)
- **Traces**: Backend → Tempo (via OTLP gRPC)
- **Visualization**: Grafana queries all three sources

### 5. Key Design Decisions

1. **Docker Compose**: All services containerized for easy deployment
2. **OpenTelemetry**: Industry-standard observability framework
3. **Structured Logging**: JSON format for better parsing and correlation
4. **Anomaly Injection**: Built-in mechanisms for testing observability
5. **Load Testing**: k6 scripts for realistic traffic simulation

### 6. Scalability Considerations

- **Horizontal Scaling**: Stateless backend allows multiple instances
- **Database Connection Pooling**: Handles concurrent connections efficiently
- **Observability Overhead**: Minimal impact on application performance
- **Resource Management**: Proper connection limits and timeouts

### 7. Security Considerations

- **JWT Tokens**: Secure authentication mechanism
- **Password Hashing**: bcrypt for password storage
- **Input Validation**: Pydantic schemas for request validation
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection

### 8. Monitoring & Alerting Strategy

- **Health Checks**: `/health` endpoint for service status
- **Metrics Thresholds**: Configurable in Grafana
- **Error Tracking**: Comprehensive error logging and metrics
- **Performance Monitoring**: Latency percentiles and slow query tracking


