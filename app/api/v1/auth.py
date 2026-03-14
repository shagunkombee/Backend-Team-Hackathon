"""
Authentication endpoints
"""
import random
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from opentelemetry import trace
import structlog

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token

router = APIRouter()
logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """User registration endpoint"""
    with tracer.start_as_current_span("auth.register") as span:
        span.set_attribute("user.username", user_data.username)
        span.set_attribute("user.email", user_data.email)
        
        logger.info("Registration attempt", username=user_data.username, email=user_data.email)
        
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            logger.warning("Registration failed - user exists", username=user_data.username)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "UserExists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info("User registered successfully", user_id=new_user.id, username=new_user.username)
        span.set_attribute("user.id", new_user.id)
        
        return new_user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """User login endpoint"""
    with tracer.start_as_current_span("auth.login") as span:
        span.set_attribute("user.username", credentials.username)
        
        logger.info("Login attempt", username=credentials.username)
        
        # Find user
        user = db.query(User).filter(User.username == credentials.username).first()
        
        if not user:
            logger.warning("Login failed - user not found", username=credentials.username)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "UserNotFound")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            logger.warning("Login failed - invalid password", username=credentials.username)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "InvalidPassword")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning("Login failed - user inactive", username=credentials.username)
            span.set_attribute("error", True)
            span.set_attribute("error.type", "UserInactive")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Inject anomaly: random errors if enabled
        if settings.ENABLE_RANDOM_ERRORS and random.random() < settings.RANDOM_ERROR_RATE:
            logger.error("Anomaly injected - random login error", username=credentials.username)
            span.set_attribute("anomaly.injected", True)
            span.set_attribute("anomaly.type", "RandomError")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Random error injected for testing"
            )
        
        # Inject anomaly: artificial delay if enabled
        if settings.ENABLE_ANOMALY_DELAY:
            delay = settings.ANOMALY_DELAY_SECONDS
            logger.warning("Anomaly injected - artificial delay", delay_seconds=delay)
            span.set_attribute("anomaly.injected", True)
            span.set_attribute("anomaly.type", "ArtificialDelay")
            span.set_attribute("anomaly.delay_seconds", delay)
            time.sleep(delay)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        
        logger.info("Login successful", user_id=user.id, username=user.username)
        span.set_attribute("user.id", user.id)
        span.set_attribute("login.success", True)
        
        return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    with tracer.start_as_current_span("auth.get_current_user"):
        return current_user


