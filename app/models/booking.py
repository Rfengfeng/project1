from enum import Enum
from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date, func, Enum as DBEnum, null
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import schedule


class BookingStatus(Enum):
  pending = 'pending'
  confirmed = 'confirmed'
  cancelled = 'cancelled'


class Booking(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[Integer] = mapped_column(ForeignKey(
      'user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
  user = relationship('User', back_populates='bookings')
  type: Mapped[String] = mapped_column(String(32), nullable=True)
  cost: Mapped[Numeric] = mapped_column(Numeric(8, 2), default=0)
  amount_paid: Mapped[Numeric] = mapped_column(Numeric(8, 2), default=0)

  schedule_id: Mapped[Integer] = mapped_column(ForeignKey(
      'schedule.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
  schedule = relationship('Schedule', back_populates='bookings')

  start_datetime: Mapped[DateTime] = mapped_column(DateTime)
  end_datetime: Mapped[DateTime] = mapped_column(DateTime)
  created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

  payments = relationship('Payment', back_populates='booking')
  status: Mapped[String] = mapped_column(DBEnum(
      BookingStatus.pending.value,
      BookingStatus.confirmed.value,
      BookingStatus.cancelled.value
  ), default=BookingStatus.pending.value)

  reminders = relationship('Reminder', back_populates='booking')
  attended = mapped_column(Boolean, default=False)
