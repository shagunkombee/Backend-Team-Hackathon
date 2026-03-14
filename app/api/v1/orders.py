"""
Order endpoints
"""
import time
import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from opentelemetry import trace
import structlog

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter()
logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    with tracer.start_as_current_span("orders.create") as span:
        span.set_attribute("order.user_id", current_user.id)
        span.set_attribute("order.items_count", len(order_data.items))
        
        logger.info("Creating order", user_id=current_user.id, items_count=len(order_data.items))
        
        # Validate items
        if not order_data.items:
            logger.warning("Order creation failed - no items", user_id=current_user.id)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "ValidationError")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must contain at least one item"
            )
        
        # Calculate total and validate products
        total_amount = 0.0
        order_items_data = []
        
        with tracer.start_as_current_span("orders.validate_items") as validate_span:
            for item_data in order_data.items:
                product = db.query(Product).filter(Product.id == item_data.product_id).first()
                
                if not product:
                    logger.warning("Order creation failed - product not found", product_id=item_data.product_id)
                    validate_span.set_attribute("error", True)
                    span.set_attribute("error", True)
                    span.set_attribute("error.type", "ProductNotFound")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Product {item_data.product_id} not found"
                    )
                
                if product.stock_quantity < item_data.quantity:
                    logger.warning("Order creation failed - insufficient stock", 
                                 product_id=item_data.product_id, 
                                 requested=item_data.quantity, 
                                 available=product.stock_quantity)
                    validate_span.set_attribute("error", True)
                    span.set_attribute("error", True)
                    span.set_attribute("error.type", "InsufficientStock")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for product {product.name}"
                    )
                
                item_total = item_data.price * item_data.quantity
                total_amount += item_total
                order_items_data.append((product, item_data))
        
        span.set_attribute("order.total_amount", total_amount)
        
        # Inject anomaly: artificial delay
        if settings.ENABLE_ANOMALY_DELAY:
            delay = settings.ANOMALY_DELAY_SECONDS
            logger.warning("Anomaly injected - artificial delay", delay_seconds=delay)
            span.set_attribute("anomaly.injected", True)
            span.set_attribute("anomaly.type", "ArtificialDelay")
            span.set_attribute("anomaly.delay_seconds", delay)
            time.sleep(delay)
        
        # Inject anomaly: random errors
        if settings.ENABLE_RANDOM_ERRORS and random.random() < settings.RANDOM_ERROR_RATE:
            logger.error("Anomaly injected - random order error", user_id=current_user.id)
            span.set_attribute("anomaly.injected", True)
            span.set_attribute("anomaly.type", "RandomError")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Random error injected for testing"
            )
        
        # Create order
        with tracer.start_as_current_span("orders.create_db_transaction") as db_span:
            new_order = Order(
                user_id=current_user.id,
                total_amount=total_amount,
                shipping_address=order_data.shipping_address,
                status=OrderStatus.PENDING
            )
            db.add(new_order)
            db.flush()  # Get order ID
            
            # Create order items and update stock
            for product, item_data in order_items_data:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=product.id,
                    quantity=item_data.quantity,
                    price=item_data.price
                )
                db.add(order_item)
                
                # Update product stock
                product.stock_quantity -= item_data.quantity
            
            db.commit()
            db.refresh(new_order)
        
        logger.info("Order created", order_id=new_order.id, user_id=current_user.id, total=total_amount)
        span.set_attribute("order.id", new_order.id)
        
        return new_order


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List orders with pagination and filtering"""
    with tracer.start_as_current_span("orders.list") as span:
        span.set_attribute("pagination.skip", skip)
        span.set_attribute("pagination.limit", limit)
        span.set_attribute("order.user_id", current_user.id)
        
        logger.info("Listing orders", user_id=current_user.id, skip=skip, limit=limit)
        
        # Build query
        query = db.query(Order).filter(Order.user_id == current_user.id)
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
            span.set_attribute("filter.status", status_filter.value)
        
        # Get total count
        total = query.count()
        span.set_attribute("pagination.total", total)
        
        # Apply pagination
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.info("Orders listed", count=len(orders), total=total, user_id=current_user.id)
        
        return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single order by ID"""
    with tracer.start_as_current_span("orders.get") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.user_id", current_user.id)
        
        logger.info("Getting order", order_id=order_id, user_id=current_user.id)
        
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).first()
        
        if not order:
            logger.warning("Order not found", order_id=order_id, user_id=current_user.id)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "NotFound")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return order

