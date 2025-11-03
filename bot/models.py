"""Database models for GPSkilledGuardian."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class PaymentStatus(enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    CONFIRMING = "confirming"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


class PaymentType(enum.Enum):
    """Payment type enumeration."""
    BTC = "btc"
    LTC = "ltc"
    OSRS_GP = "osrs_gp"


class Payment(Base):
    """Payment tracking model."""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    amount_usd = Column(Float, nullable=False)
    amount_crypto = Column(Float, nullable=True)  # For BTC/LTC
    amount_gp = Column(Float, nullable=True)  # For OSRS GP
    wallet_address = Column(String, nullable=True)  # Recipient address for crypto
    payment_address = Column(String, nullable=True)  # User's payment address
    transaction_id = Column(String, nullable=True, index=True)  # Transaction hash or trade ID
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    confirmations = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)


class OSRSTrade(Base):
    """OSRS trade tracking model."""
    __tablename__ = "osrs_trades"
    
    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    rsn = Column(String, nullable=False)  # RuneScape Name
    gp_amount = Column(Float, nullable=False)
    world = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    trade_started_at = Column(DateTime, nullable=True)
    trade_completed_at = Column(DateTime, nullable=True)
    screenshot_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)


class User(Base):
    """User model for tracking Discord users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False)
    discriminator = Column(String, nullable=True)
    has_paid_role = Column(Boolean, default=False)
    total_payments = Column(Integer, default=0)
    total_spent_usd = Column(Float, default=0.0)
    osrs_rsn = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_payment_at = Column(DateTime, nullable=True)


class ModerationAction(Base):
    """Moderation action tracking."""
    __tablename__ = "moderation_actions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    moderator_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)  # warn, mute, kick, ban
    reason = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in minutes for mute
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class WebhookLog(Base):
    """Webhook event logging."""
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True)
    webhook_type = Column(String, nullable=False)  # payment, blockcypher, etc.
    payload = Column(Text, nullable=False)
    status = Column(String, default="received")  # received, processed, failed
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)
