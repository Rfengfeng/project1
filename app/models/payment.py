from enum import Enum
from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date, Enum as DBEnum, false
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.models import booking, subscription


class PaymentStatus(Enum):
  pending = 'pending'
  completed = 'completed'
  failed = 'failed'
  refunded = 'refunded'


class Payment(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  first_name: Mapped[String] = mapped_column(String(32))
  last_name: Mapped[String] = mapped_column(String(32))
  email: Mapped[String] = mapped_column(String(255), nullable=True)
  address: Mapped[String] = mapped_column(String(255), nullable=True)
  address2: Mapped[String] = mapped_column(String(255), nullable=True)
  country: Mapped[String] = mapped_column(String(64), nullable=True)
  state: Mapped[String] = mapped_column(String(64), nullable=True)
  suburb: Mapped[String] = mapped_column(String(64), nullable=True)
  postcode: Mapped[String] = mapped_column(String(32), nullable=True)
  payment_type: Mapped[String] = mapped_column(String(64), nullable=True)
  paid_at: Mapped[DateTime] = mapped_column(
      DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
  status: Mapped[Enum] = mapped_column(DBEnum(
      'pending', 'completed', 'failed', 'refunded'), default='pending', nullable=False)

  name_on_card: Mapped[String] = mapped_column(String(255))
  card_number: Mapped[String] = mapped_column(String(4))
  expiration_date: Mapped[String] = mapped_column(String(25), nullable=True)

  user_id: Mapped[Integer] = mapped_column(ForeignKey(
      'user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
  user = relationship('User', back_populates='payments')

  user_subscription_id: Mapped[Integer] = mapped_column(ForeignKey(
      'user_subscription.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
  user_subscription = relationship(
      'UserSubscription', back_populates='payments')

  booking_id: Mapped[Integer] = mapped_column(ForeignKey(
      'booking.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
  booking = relationship('Booking', back_populates='payments')

  refunded_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
  refunded_amount: Mapped[Numeric] = mapped_column(
      Numeric(10, 2), nullable=True)
  amount_paid: Mapped[Numeric] = mapped_column(
      Numeric(10, 2), nullable=False, server_default='0.00')
