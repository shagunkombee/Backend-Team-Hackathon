"""
Product endpoints
"""
import time
import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from opentelemetry import trace
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()
logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product"""
    with tracer.start_as_current_span("products.create") as span:
        span.set_attribute("product.name", product_data.name)
        span.set_attribute("product.price", product_data.price)
        
        logger.info("Creating product", name=product_data.name, price=product_data.price)
        
        # Validation
        if product_data.price < 0:
            logger.warning("Product creation failed - invalid price", price=product_data.price)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "ValidationError")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price cannot be negative"
            )
        
        # Inject anomaly: artificial delay
        if settings.ENABLE_ANOMALY_DELAY:
            delay = settings.ANOMALY_DELAY_SECONDS
            logger.warning("Anomaly injected - artificial delay", delay_seconds=delay)
            span.set_attribute("anomaly.injected", True)
            span.set_attribute("anomaly.type", "ArtificialDelay")
            time.sleep(delay)
        
        # Create product
        new_product = Product(**product_data.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        logger.info("Product created", product_id=new_product.id, name=new_product.name)
        span.set_attribute("product.id", new_product.id)
        
        return new_product


@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """List products with pagination and filtering"""
    with tracer.start_as_current_span("products.list") as span:
        span.set_attribute("pagination.skip", skip)
        span.set_attribute("pagination.limit", limit)
        
        logger.info("Listing products", skip=skip, limit=limit, category=category, search=search)
        
        # Build query
        query = db.query(Product)
        
        # Apply filters
        if category:
            query = query.filter(Product.category == category)
            span.set_attribute("filter.category", category)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
            span.set_attribute("filter.search", search)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
            span.set_attribute("filter.min_price", min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
            span.set_attribute("filter.max_price", max_price)
        
        # Inject anomaly: inefficient query (no index usage simulation)
        # This is a simple way to simulate slow queries
        if settings.ENABLE_ANOMALY_DELAY:
            delay = settings.ANOMALY_DELAY_SECONDS * 0.5
            time.sleep(delay)
        
        # Get total count
        total = query.count()
        span.set_attribute("pagination.total", total)
        
        # Apply pagination
        products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.info("Products listed", count=len(products), total=total)
        
        return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID"""
    with tracer.start_as_current_span("products.get") as span:
        span.set_attribute("product.id", product_id)
        
        logger.info("Getting product", product_id=product_id)
        
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            logger.warning("Product not found", product_id=product_id)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "NotFound")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product"""
    with tracer.start_as_current_span("products.update") as span:
        span.set_attribute("product.id", product_id)
        
        logger.info("Updating product", product_id=product_id)
        
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            logger.warning("Product not found for update", product_id=product_id)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "NotFound")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Update fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        logger.info("Product updated", product_id=product_id)
        
        return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product"""
    with tracer.start_as_current_span("products.delete") as span:
        span.set_attribute("product.id", product_id)
        
        logger.info("Deleting product", product_id=product_id)
        
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            logger.warning("Product not found for deletion", product_id=product_id)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "NotFound")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        db.delete(product)
        db.commit()
        
        logger.info("Product deleted", product_id=product_id)


