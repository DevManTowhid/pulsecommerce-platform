from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class wishlist_items(Base):
    __tablename__ = "wishlist_items"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)


# --- MODELS ---

class OrderItem(Base):
    """
    The Association Object: The 'Amount' and 'Price at Purchase' live here.
    This tracks exactly what was bought, how many, and for how much.
    """
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    
    quantity = Column(Integer, default=1, nullable=False)
    price_at_purchase = Column(Float, nullable=False) # Historical record

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_links")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    orders = relationship("Order", back_populates="owner")
    reviews = relationship("Review", back_populates="user")
    wishlist = relationship("Product", back_populates="wishlist_items")
    notifications = relationship("Notification", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False) # Current live price
    category = Column(String, index=True)
    stock = Column(Integer, default=0)
    attributes = Column(JSON) # Flexible: {"color": "Midnight Blue", "size": "XL"}
    
    # Relationships
    order_links = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float, nullable=False)
    status = Column(String, default="pending") # pending, paid, shipped, cancelled
    shipping_address = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer) # 1 to 5
    comment = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")


# --- INTERMEDIATE/ENGINEERING MODELS ---

class InventoryReservation(Base):
    """Prevents race conditions by 'holding' stock for a limited time."""
    __tablename__ = "inventory_reservations"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime)


class AuditLog(Base):
    """High-level traceability for security and debugging."""
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    target_type = Column(String) # e.g., 'ORDER'
    target_id = Column(Integer)
    action = Column(String) # e.g., 'STATUS_UPGRADED_TO_SHIPPED'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column(JSON) # Store 'before' and 'after' snapshots