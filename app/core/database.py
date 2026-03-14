"""
Database Configuration and Session Management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import time
from prometheus_client import Histogram
from opentelemetry import trace

from app.core.config import settings

# Database URL
DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Prometheus metrics for DB
DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table']
)


# Database query instrumentation
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query start time"""
    context._query_start_time = time.time()


@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query duration and create span"""
    if hasattr(context, '_query_start_time'):
        duration = time.time() - context._query_start_time
        
        # Extract table name from statement (simple extraction)
        table_name = "unknown"
        statement_lower = statement.lower()
        if "insert into" in statement_lower:
            table_name = statement_lower.split("insert into")[1].split()[0]
            operation = "insert"
        elif "select" in statement_lower:
            table_name = statement_lower.split("from")[1].split()[0] if "from" in statement_lower else "unknown"
            operation = "select"
        elif "update" in statement_lower:
            table_name = statement_lower.split("update")[1].split()[0]
            operation = "update"
        elif "delete" in statement_lower:
            table_name = statement_lower.split("from")[1].split()[0] if "from" in statement_lower else "unknown"
            operation = "delete"
        else:
            operation = "other"
        
        # Record metric
        DB_QUERY_DURATION.labels(operation=operation, table=table_name).observe(duration)
        
        # Create trace span for DB query
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(
            f"db.{operation}",
            attributes={
                "db.operation": operation,
                "db.table": table_name,
                "db.duration_ms": round(duration * 1000, 2),
                "db.statement": statement[:200]  # Limit statement length
            }
        ):
            pass


def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

