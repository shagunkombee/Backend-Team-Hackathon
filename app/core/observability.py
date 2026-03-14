"""
OpenTelemetry Observability Setup
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings

# Setup file logging for Promtail
log_dir = "/var/log/app"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "backend.log")

# Configure file handler
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Add file handler to root logger
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.setLevel(logging.INFO)


def setup_observability():
    """Setup OpenTelemetry tracing and instrumentation"""
    
    # Create resource with service information
    resource = Resource.create({
        "service.name": "hackathon-backend",
        "service.version": "1.0.0",
        "service.namespace": "hackathon",
    })
    
    # Setup tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    # Setup OTLP exporter for Tempo
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument SQLAlchemy
    from app.core.database import engine
    SQLAlchemyInstrumentor().instrument(engine=engine)
    
    logger = structlog.get_logger()
    logger.info("Observability setup completed", service="backend")


