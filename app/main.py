"""
FastAPI Main Application
Hackathon Backend - Observability Focus
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.core.observability import setup_observability
from app.api.v1 import api_router

# Prometheus metrics
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

ACTIVE_USERS = Gauge(
    'active_users_total',
    'Number of active users'
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting application", service="backend")
    Base.metadata.create_all(bind=engine)
    setup_observability()
    logger.info("Application started successfully", service="backend")
    yield
    # Shutdown
    logger.info("Shutting down application", service="backend")


app = FastAPI(
    title="Hackathon Backend API",
    description="Observability-focused backend with FastAPI, MySQL, and full observability stack",
    version="1.0.0",
    lifespan=lifespan
)

# Setup OpenTelemetry instrumentation
FastAPIInstrumentor.instrument_app(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for metrics and logging
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Middleware for metrics, logging, and tracing"""
    tracer = trace.get_tracer(__name__)
    start_time = time.time()
    
    # Extract trace context
    span = tracer.start_span(
        name=f"{request.method} {request.url.path}",
        attributes={
            "http.method": request.method,
            "http.url": str(request.url),
            "http.route": request.url.path,
        }
    )
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        # Log request
        logger.info(
            "HTTP request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            trace_id=format(span.get_span_context().trace_id, '032x') if span.get_span_context().trace_id else None
        )
        
        # Add trace ID to response headers
        if span.get_span_context().trace_id:
            response.headers["X-Trace-ID"] = format(span.get_span_context().trace_id, '032x')
        
        span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("http.duration_ms", round(duration * 1000, 2))
        
        return response
        
    except Exception as e:
        ERROR_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            error_type=type(e).__name__
        ).inc()
        
        logger.error(
            "HTTP request error",
            method=request.method,
            path=request.url.path,
            error=str(e),
            error_type=type(e).__name__,
            trace_id=format(span.get_span_context().trace_id, '032x') if span.get_span_context().trace_id else None
        )
        
        span.record_exception(e)
        span.set_attribute("http.status_code", 500)
        raise
        
    finally:
        span.end()


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hackathon-backend",
        "version": "1.0.0"
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")

