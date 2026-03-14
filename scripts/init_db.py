"""
Database initialization script
Creates tables and seeds initial data
"""
import sys
import os

# Add app directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(os.path.dirname(script_dir), 'app')
sys.path.insert(0, os.path.dirname(app_dir))

from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.core.security import get_password_hash

def init_db():
    """Initialize database with tables and seed data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@hackathon.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✓ Admin user created (username: admin, password: admin123)")
        
        # Create test products
        product_count = db.query(Product).count()
        if product_count == 0:
            products = [
                Product(name="Laptop", description="High-performance laptop", price=999.99, stock_quantity=50, category="Electronics"),
                Product(name="Mouse", description="Wireless mouse", price=29.99, stock_quantity=100, category="Electronics"),
                Product(name="Keyboard", description="Mechanical keyboard", price=79.99, stock_quantity=75, category="Electronics"),
                Product(name="Monitor", description="27-inch 4K monitor", price=399.99, stock_quantity=30, category="Electronics"),
                Product(name="Headphones", description="Noise-cancelling headphones", price=199.99, stock_quantity=60, category="Audio"),
            ]
            for product in products:
                db.add(product)
            db.commit()
            print(f"✓ Created {len(products)} test products")
        
        print("✓ Database initialization completed")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()


